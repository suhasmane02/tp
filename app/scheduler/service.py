import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import settings
from app.database.session import SessionLocal
from app.models import Channel, CompetitorChannel
from app.ingestion.service import sync_channel
scheduler=BackgroundScheduler(timezone='UTC')
def public_sync():
 db=SessionLocal()
 try:
  for c in db.query(Channel).all():
   try: asyncio.run(sync_channel(db,c.channel_id,db.get(CompetitorChannel,c.channel_id) is not None))
   except Exception: pass
 finally: db.close()
def start_scheduler():
 scheduler.add_job(public_sync,'cron',id='public_sync',replace_existing=True,**dict(zip(['minute','hour','day','month','day_of_week'],settings.public_sync_cron.split())))
 scheduler.start()
