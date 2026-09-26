from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'sqlite:///./data/youtube_analytics.db'
    youtube_api_key: str = ''
    google_client_id: str = ''
    google_client_secret: str = ''
    google_redirect_uri: str = 'http://localhost:8000/api/oauth/callback'
    app_secret_key: str = 'development-only-change-me'
    public_sync_cron: str = '0 */6 * * *'
    analytics_sync_cron: str = '20 5 * * *'
    competitor_sync_cron: str = '40 5 * * *'
    daily_analysis_cron: str = '0 6 * * *'
    youtube_daily_quota_budget: int = 10000
    mock_mode: bool = False
    raw_data_dir: Path = Path('data/raw/youtube')
settings = Settings()
