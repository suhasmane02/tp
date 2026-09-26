from datetime import datetime,timezone,timedelta
from app.models import Channel,Video,VideoSnapshot,CompetitorChannel,Alert
from app.analytics.engine import classify,derive
def seed(db):
 if db.get(Channel,'UC_DEMO_OWN'): return
 now=datetime.now(timezone.utc)
 for ci,name,own in [('UC_DEMO_OWN','Maharashtra Family Vlogs',True),('UC_DEMO_COMP1','Pune Family Adventures',False),('UC_DEMO_COMP2','Marathi Village Stories',False),('UC_DEMO_COMP3','Mumbai Daily Life',False)]:
  c=Channel(channel_id=ci,channel_name=name,channel_url='https://youtube.com/@demo',is_own=own,subscriber_count=12500,view_count=800000,video_count=8);db.add(c)
  if not own:db.add(CompetitorChannel(channel_id=ci,label=name))
  for n in range(8):
   sec=50 if n%2==0 else 720;title=('#Shorts ' if n%2==0 else '')+['Family trip to Lonavala','Ganpati celebration with grandparents','Village food vlog','Mumbai shopping day'][n%4];fmt,con,reason=classify(sec,'none',title);v=Video(video_id=f'{ci[-3:]}_{n}',channel_id=ci,title=title,video_url='https://youtube.com/watch?v=demo',published_at=now-timedelta(days=n+1),duration_seconds=sec,view_count=(n+1)*1400,like_count=(n+1)*90,comment_count=(n+1)*12,format_classification=fmt,classification_confidence=con,classification_reason=reason,is_short=fmt=='short',is_long_form=fmt=='long_form');db.add(v);db.flush()
   for d in range(4):db.add(VideoSnapshot(video_id=v.video_id,snapshot_timestamp=now-timedelta(days=3-d),view_count=max(1,v.view_count-(3-d)*300),like_count=v.like_count,comment_count=v.comment_count))
   derive(db,v)
 db.add(Alert(alert_type='NEW_VIDEO',message='Demo: a new family-trip video was discovered.',dedupe_key='demo-new'));db.commit()
