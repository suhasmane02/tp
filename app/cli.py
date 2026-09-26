import argparse,asyncio,csv,json
from pathlib import Path
from sqlalchemy import select
from app.database.base import Base
from app.database.session import engine,SessionLocal
from app.models import Channel,Video
from app.ingestion.service import sync_channel
from app.demo import seed
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True);a=sub.add_parser('add-channel');a.add_argument('identifier');a.add_argument('--competitor',action='store_true');s=sub.add_parser('sync-channel');s.add_argument('channel_id');sub.add_parser('sync');sub.add_parser('list-channels');sub.add_parser('seed-demo');e=sub.add_parser('export');e.add_argument('--channel');e.add_argument('--format',choices=['csv','json'],default='csv');sub.add_parser('status');args=p.parse_args();Base.metadata.create_all(engine);db=SessionLocal()
 try:
  if args.cmd=='seed-demo':seed(db)
  elif args.cmd=='add-channel':asyncio.run(sync_channel(db,args.identifier,args.competitor))
  elif args.cmd=='sync-channel':asyncio.run(sync_channel(db,args.channel_id))
  elif args.cmd=='sync':
   for c in db.scalars(select(Channel)):asyncio.run(sync_channel(db,c.channel_id))
  elif args.cmd=='list-channels':print('\n'.join(f'{c.channel_id}\t{c.channel_name}' for c in db.scalars(select(Channel))))
  elif args.cmd=='status':print(json.dumps({'channels':db.query(Channel).count(),'videos':db.query(Video).count()}))
  elif args.cmd=='export':
   rows=db.scalars(select(Video).where(Video.channel_id==args.channel) if args.channel else select(Video)).all();Path('data/exports').mkdir(parents=True,exist_ok=True);fn=Path('data/exports/videos.'+args.format)
   if args.format=='json':fn.write_text(json.dumps([{'video_id':v.video_id,'title':v.title,'views':v.view_count} for v in rows],indent=2))
   else:
    with fn.open('w',newline='',encoding='utf8') as f:w=csv.writer(f);w.writerow(['video_id','title','views','likes','comments']);w.writerows((v.video_id,v.title,v.view_count,v.like_count,v.comment_count) for v in rows)
   print(fn)
 finally:db.close()
if __name__=='__main__':main()
