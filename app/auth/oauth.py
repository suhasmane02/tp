"""Minimal OAuth 2.0 authorization-code flow; tokens stay in a local file, never PostgreSQL."""
import json,secrets
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlencode
import httpx
from app.config import settings
SCOPES=['https://www.googleapis.com/auth/yt-analytics.readonly','https://www.googleapis.com/auth/youtube.readonly']
TOKEN_PATH=Path('data/oauth-token.json'); STATE_PATH=Path('data/oauth-state.txt')
def authorization_url():
 if not settings.google_client_id or not settings.google_client_secret: raise ValueError('GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are required')
 state=secrets.token_urlsafe(32);STATE_PATH.parent.mkdir(parents=True,exist_ok=True);STATE_PATH.write_text(state)
 return 'https://accounts.google.com/o/oauth2/v2/auth?'+urlencode({'client_id':settings.google_client_id,'redirect_uri':settings.google_redirect_uri,'response_type':'code','scope':' '.join(SCOPES),'access_type':'offline','prompt':'consent','state':state})
async def exchange(code,state):
 if not STATE_PATH.exists() or not secrets.compare_digest(STATE_PATH.read_text(),state): raise ValueError('OAuth state validation failed')
 async with httpx.AsyncClient(timeout=30) as c:r=await c.post('https://oauth2.googleapis.com/token',data={'code':code,'client_id':settings.google_client_id,'client_secret':settings.google_client_secret,'redirect_uri':settings.google_redirect_uri,'grant_type':'authorization_code'})
 if r.is_error:raise ValueError('Token exchange failed: '+r.text[:250])
 token=r.json();TOKEN_PATH.write_text(json.dumps(token));return token
