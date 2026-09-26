from datetime import datetime, timezone
from statistics import median
from sqlalchemy import select
from app.models import Video, VideoSnapshot, DerivedVideoFeature, Alert
TAXONOMY=['family_daily_life','family_comedy','family_trip','maharashtra_travel','village_life','food','festival','ganpati','diwali','monsoon','shopping','family_challenge','husband_wife','children','grandparents','emotional','surprise','birthday','wedding','family_event','local_culture','lifestyle']
def classify(duration, live, title=''):
 if live and live != 'none': return ('live',.98,'YouTube liveBroadcastContent indicates a live broadcast')
 # Public Data API has no reliable Shorts flag. URL/title hint plus <=180s is explicit and conservative.
 if duration and duration <=180 and '#shorts' in title.lower(): return ('short',.8,'Duration <= 180 seconds and title includes #Shorts; public API does not expose a definitive Shorts flag')
 if duration and duration >180: return ('long_form',.95,'Duration exceeds 180 seconds')
 return ('unknown',.25,'Public metadata cannot reliably determine format')
def derive(db, video):
 snaps=db.scalars(select(VideoSnapshot).where(VideoSnapshot.video_id==video.video_id).order_by(VideoSnapshot.snapshot_timestamp)).all()
 now=datetime.now(timezone.utc); age=max((now-video.published_at).total_seconds()/86400,1/24) if video.published_at else 1
 views_per_day=video.view_count/age; velocity=0; acceleration=0
 if len(snaps)>=2:
  dt=max((snaps[-1].snapshot_timestamp-snaps[-2].snapshot_timestamp).total_seconds()/3600,1/60); velocity=(snaps[-1].view_count-snaps[-2].view_count)/dt
  if len(snaps)>=3:
   olddt=max((snaps[-2].snapshot_timestamp-snaps[-3].snapshot_timestamp).total_seconds()/3600,1/60); acceleration=velocity-(snaps[-2].view_count-snaps[-3].view_count)/olddt
 topic=next((x for x in TAXONOMY if x.replace('_',' ') in video.title.lower() or x.split('_')[0] in video.title.lower()),None)
 peers=db.scalars(select(Video.view_count).where(Video.channel_id==video.channel_id)).all(); med=median(peers) if peers else 0
 score=min(100, max(0, 50*(video.view_count/(med or 1)) + 20*((video.like_count or 0)*1000/max(video.view_count,1)) + min(30,velocity)))
 feature=db.get(DerivedVideoFeature,video.video_id) or DerivedVideoFeature(video_id=video.video_id); feature.topic=topic; feature.local_performance_index=round(score,2); feature.features={'duration_bucket':'short' if (video.duration_seconds or 0)<=180 else 'long','title_length':len(video.title),'views_per_day':round(views_per_day,2),'views_per_hour':round(velocity,2),'growth_acceleration':round(acceleration,2),'likes_per_1000_views':round((video.like_count or 0)*1000/max(video.view_count,1),2),'comments_per_1000_views':round((video.comment_count or 0)*1000/max(video.view_count,1),2),'model_notice':'Internal analytical model — not a YouTube ranking score.'}; db.add(feature); return feature
