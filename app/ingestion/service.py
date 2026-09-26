from datetime import datetime, timezone
from sqlalchemy import select
from app.models import Channel, Video, VideoSnapshot, ChannelSnapshot, CompetitorChannel, IngestionRun, Alert
from app.youtube.client import YouTubeDataClient
from app.analytics.engine import classify, derive

def duration_seconds(value):
 import re
 m=re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',value or ''); return (int(m.group(1) or 0)*3600+int(m.group(2) or 0)*60+int(m.group(3) or 0)) if m else None
def dt(s): return datetime.fromisoformat(s.replace('Z','+00:00')) if s else None
async def sync_channel(db, identifier, competitor=False):
 run=IngestionRun(job_name='public_sync',channel_id=identifier); db.add(run); db.commit(); client=YouTubeDataClient()
 try:
  raw=await client.resolve_channel(identifier); sn=raw['snippet']; cd=raw.get('contentDetails',{}).get('relatedPlaylists',{}); st=raw.get('statistics',{}); cid=raw['id']; c=db.get(Channel,cid) or Channel(channel_id=cid,channel_name=sn['title']); c.channel_url=f'https://www.youtube.com/channel/{cid}'; c.channel_handle=sn.get('customUrl'); c.description=sn.get('description'); c.published_at=dt(sn.get('publishedAt')); c.country=sn.get('country'); c.default_language=sn.get('defaultLanguage'); c.thumbnails=sn.get('thumbnails',{}); c.uploads_playlist_id=cd.get('uploads'); c.subscriber_count=int(st['subscriberCount']) if st.get('subscriberCount') else None; c.view_count=int(st.get('viewCount',0)); c.video_count=int(st.get('videoCount',0)); c.hidden_subscriber_count=st.get('hiddenSubscriberCount',False); c.last_fetched_at=datetime.now(timezone.utc); db.add(c); db.flush(); db.add(ChannelSnapshot(channel_id=cid,subscriber_count=c.subscriber_count,view_count=c.view_count,video_count=c.video_count));
  if competitor: db.merge(CompetitorChannel(channel_id=cid))
  ids=await client.upload_ids(c.uploads_playlist_id); run.records_found=len(ids)
  for item in await client.videos(ids):
   s=item['snippet']; vs=item.get('statistics',{}); sec=duration_seconds(item.get('contentDetails',{}).get('duration')); fmt,confidence,reason=classify(sec,item.get('snippet',{}).get('liveBroadcastContent'),s.get('title','')); v=db.get(Video,item['id']) or Video(video_id=item['id'],channel_id=cid,title=s['title'],video_url=f"https://www.youtube.com/watch?v={item['id']}"); v.title=s['title'];v.description=s.get('description');v.published_at=dt(s.get('publishedAt'));v.duration_seconds=sec;v.tags=s.get('tags',[]);v.thumbnails=s.get('thumbnails',{});v.live_broadcast_content=s.get('liveBroadcastContent');v.view_count=int(vs.get('viewCount',0));v.like_count=int(vs['likeCount']) if vs.get('likeCount') else None;v.comment_count=int(vs['commentCount']) if vs.get('commentCount') else None;v.format_classification=fmt;v.classification_confidence=confidence;v.classification_reason=reason;v.is_short=fmt=='short';v.is_long_form=fmt=='long_form';v.is_live=fmt=='live';v.last_fetched_at=datetime.now(timezone.utc);db.add(v);db.flush();db.add(VideoSnapshot(video_id=v.video_id,view_count=v.view_count,like_count=v.like_count,comment_count=v.comment_count));derive(db,v);run.records_updated+=1
  run.status='success'; run.finished_at=datetime.now(timezone.utc);db.commit(); return c
 except Exception as e:
  run.status='failed';run.error=str(e);run.finished_at=datetime.now(timezone.utc);db.add(Alert(alert_type='INGESTION_FAILURE',channel_id=identifier,message=str(e),dedupe_key=f'ingest:{identifier}:{datetime.now(timezone.utc).date()}'));db.commit();raise
