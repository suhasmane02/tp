from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import *
from app.ingestion.service import sync_channel
from app.config import settings
router=APIRouter(prefix='/api')
class AddChannel(BaseModel): identifier:str; competitor:bool=False; label:str|None=None
@router.get('/channels')
def channels(db:Session=Depends(get_db)): return db.scalars(select(Channel).order_by(Channel.channel_name)).all()
@router.post('/channels')
async def add_channel(body:AddChannel,db:Session=Depends(get_db)):
 c=await sync_channel(db,body.identifier,body.competitor)
 if body.competitor: db.merge(CompetitorChannel(channel_id=c.channel_id,label=body.label));db.commit()
 return {'channel_id':c.channel_id,'status':'synchronized'}
@router.get('/channels/{channel_id}')
def channel(channel_id:str,db:Session=Depends(get_db)):
 c=db.get(Channel,channel_id)
 if not c: raise HTTPException(404,'Channel not found')
 return c
@router.delete('/channels/{channel_id}')
def delete_channel(channel_id:str,db:Session=Depends(get_db)):
 c=db.get(Channel,channel_id)
 if not c: raise HTTPException(404,'Channel not found')
 db.delete(c);db.commit();return {'deleted':channel_id}
@router.post('/channels/{channel_id}/sync')
async def sync(channel_id:str,db:Session=Depends(get_db)): await sync_channel(db,channel_id,db.get(CompetitorChannel,channel_id) is not None);return {'status':'synchronized'}
@router.get('/channels/{channel_id}/videos')
def videos(channel_id:str,q:str|None=None,format:str|None=None,page:int=1,size:int=50,db:Session=Depends(get_db)):
 s=select(Video).where(Video.channel_id==channel_id)
 if q:s=s.where(Video.title.ilike(f'%{q}%'))
 if format:s=s.where(Video.format_classification==format)
 return db.scalars(s.order_by(Video.published_at.desc()).offset((page-1)*size).limit(size)).all()
@router.get('/videos/{video_id}')
def video(video_id:str,db:Session=Depends(get_db)):
 v=db.get(Video,video_id)
 if not v:raise HTTPException(404,'Video not found')
 return {'video':v,'derived':db.get(DerivedVideoFeature,video_id),'provenance':'DOCUMENTED_API: public statistics; DERIVED: local features.'}
@router.get('/videos/{video_id}/snapshots')
def snaps(video_id:str,db:Session=Depends(get_db)):return db.scalars(select(VideoSnapshot).where(VideoSnapshot.video_id==video_id).order_by(VideoSnapshot.snapshot_timestamp)).all()
@router.get('/competitors')
def competitors(db:Session=Depends(get_db)):return db.execute(select(Channel,CompetitorChannel).join(CompetitorChannel)).all()
@router.post('/competitors')
async def add_competitor(body:AddChannel,db:Session=Depends(get_db)): return await add_channel(AddChannel(identifier=body.identifier,competitor=True,label=body.label),db)
@router.get('/alerts')
def alerts(db:Session=Depends(get_db)):return db.scalars(select(Alert).order_by(Alert.created_at.desc()).limit(100)).all()
@router.get('/analytics/video/{video_id}')
def analytics_video(video_id:str,db:Session=Depends(get_db)):return db.get(DerivedVideoFeature,video_id) or {'status':'Unavailable'}
@router.get('/analytics/channel/{channel_id}')
def analytics_channel(channel_id:str,db:Session=Depends(get_db)):return {'snapshots':db.scalars(select(ChannelSnapshot).where(ChannelSnapshot.channel_id==channel_id).order_by(ChannelSnapshot.snapshot_timestamp)).all(),'notice':'Private Analytics API metrics require an own-channel OAuth connection.'}
@router.get('/analytics/topics')
def topics(db:Session=Depends(get_db)):return db.execute(select(DerivedVideoFeature.topic,func.count(),func.avg(Video.view_count)).join(Video).group_by(DerivedVideoFeature.topic)).all()

@router.post('/demo/seed')
def seed_demo(db:Session=Depends(get_db)):
 from app.demo import seed
 seed(db); return {'status':'demo data created'}
@router.get('/system/status')
def status(db:Session=Depends(get_db)):
 today=datetime.now(timezone.utc).date(); req=db.scalar(select(func.count(ApiRequest.id)).where(func.date(ApiRequest.requested_at)==today)) or 0; failed=db.scalar(select(func.count(IngestionRun.id)).where(IngestionRun.status=='failed')) or 0
 return {'database':'ok','youtube_api_configured':bool(settings.youtube_api_key),'oauth_status':'not_connected' if not db.scalar(select(func.count(OAuthCredentialMetadata.id))) else 'configured','scheduler':'running','requests_today':req,'quota_budget':settings.youtube_daily_quota_budget,'remaining_configured_budget':max(0,settings.youtube_daily_quota_budget-req),'failed_runs':failed}
@router.post('/oauth/start')
def oauth_start():
 from app.auth.oauth import authorization_url
 try: return {'authorization_url':authorization_url()}
 except ValueError as e: raise HTTPException(400,str(e))
@router.get('/oauth/callback')
async def oauth_callback(code:str,state:str,db:Session=Depends(get_db)):
 from app.auth.oauth import exchange,TOKEN_PATH
 try:
  token=await exchange(code,state); meta=OAuthCredentialMetadata(status='connected',scopes=token.get('scope','').split(),token_path=str(TOKEN_PATH),last_synced_at=datetime.now(timezone.utc));db.add(meta);db.commit();return {'status':'connected','message':'Authorization complete. Add/sync your channel to collect public data; authorized Analytics sync is scoped to your connected own channel.'}
 except ValueError as e: raise HTTPException(400,str(e))
