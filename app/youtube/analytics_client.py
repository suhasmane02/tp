"""Authorized YouTube Analytics reports.query client. Caller must request only documented metrics/dimensions."""
import httpx
from app.auth.oauth import TOKEN_PATH
class YouTubeAnalyticsClient:
 endpoint='https://youtubeanalytics.googleapis.com/v2/reports'
 async def query(self,start_date,end_date,metrics,dimensions=None,filters=None):
  if not TOKEN_PATH.exists(): raise RuntimeError('OAuth is not connected')
  token=__import__('json').loads(TOKEN_PATH.read_text())
  params={'ids':'channel==MINE','startDate':start_date,'endDate':end_date,'metrics':','.join(metrics)}
  if dimensions:params['dimensions']=','.join(dimensions)
  if filters:params['filters']=filters
  async with httpx.AsyncClient(timeout=30) as c:r=await c.get(self.endpoint,params=params,headers={'Authorization':'Bearer '+token['access_token']})
  r.raise_for_status();return r.json()
