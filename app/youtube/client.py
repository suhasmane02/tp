"""Official YouTube Data API v3 client; it never scrapes YouTube pages."""
import asyncio, re
from datetime import datetime
import httpx
from app.config import settings
class YouTubeApiError(RuntimeError): pass
class YouTubeDataClient:
 base='https://www.googleapis.com/youtube/v3'
 def __init__(self, key=None): self.key=key or settings.youtube_api_key
 async def _get(self, endpoint, **params):
  if not self.key: raise YouTubeApiError('YOUTUBE_API_KEY is not configured; use seed-demo or configure Google Cloud credentials.')
  params['key']=self.key
  for retry in range(4):
   async with httpx.AsyncClient(timeout=30) as client: r=await client.get(f'{self.base}/{endpoint}',params=params)
   if r.status_code in (429,500,502,503,504) and retry<3: await asyncio.sleep(2**retry); continue
   if r.is_error: raise YouTubeApiError(f'{endpoint}: {r.status_code} {r.text[:300]}')
   return r.json()
 async def resolve_channel(self, value):
  value=value.strip()
  if value.startswith('UC') and len(value)>=20: return (await self._get('channels',part='snippet,contentDetails,statistics',id=value))['items'][0]
  handle=re.search(r'(?:youtube\.com/)?@([\w.-]+)',value)
  if handle:
   data=await self._get('channels',part='snippet,contentDetails,statistics',forHandle=handle.group(1))
  else:
   data=await self._get('search',part='snippet',type='channel',q=value,maxResults=1)
   if not data['items']: raise YouTubeApiError('No channel found')
   data=await self._get('channels',part='snippet,contentDetails,statistics',id=data['items'][0]['id']['channelId'])
  if not data['items']: raise YouTubeApiError('No channel found')
  return data['items'][0]
 async def upload_ids(self, playlist_id):
  token=None; ids=[]
  while True:
   d=await self._get('playlistItems',part='contentDetails',playlistId=playlist_id,maxResults=50,**({'pageToken':token} if token else {})); ids += [x['contentDetails']['videoId'] for x in d.get('items',[])]; token=d.get('nextPageToken')
   if not token: return ids
 async def videos(self, ids):
  result=[]
  for i in range(0,len(ids),50): result += (await self._get('videos',part='snippet,contentDetails,statistics,status,liveStreamingDetails',id=','.join(ids[i:i+50])))['items']
  return result
