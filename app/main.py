from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select,func
from app.database.base import Base
from app.database.session import engine,SessionLocal
from app.models import Channel,Video,Alert
from app.api.routes import router
from app.scheduler.service import start_scheduler,scheduler
@asynccontextmanager
async def life(app):
 Base.metadata.create_all(engine);start_scheduler();yield;scheduler.shutdown(wait=False)
app=FastAPI(title='Local YouTube Vlog Analytics',lifespan=life);app.include_router(router);app.mount('/static',StaticFiles(directory='app/static'),name='static');templates=Jinja2Templates(directory='app/templates')
@app.get('/health')
def health():return {'status':'healthy'}
@app.get('/ready')
def ready():
 try:
  with engine.connect() as c:c.execute(__import__('sqlalchemy').text('select 1'))
  return {'status':'ready'}
 except Exception:return {'status':'not_ready'}
@app.get('/{path:path}',response_class=HTMLResponse)
def page(request:Request,path:str=''):
 db=SessionLocal(); channels=db.scalars(select(Channel)).all(); videos=db.scalars(select(Video).order_by(Video.published_at.desc()).limit(20)).all(); alerts=db.scalars(select(Alert).order_by(Alert.created_at.desc()).limit(10)).all();db.close();return templates.TemplateResponse('dashboard.html',{'request':request,'channels':channels,'videos':videos,'alerts':alerts,'setup':not channels,'path':path})
