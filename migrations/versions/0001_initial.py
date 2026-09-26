"""initial schema
Revision ID: 0001
"""
from alembic import op
from app.database.base import Base
import app.models
revision='0001';down_revision=None;branch_labels=None;depends_on=None
def upgrade():
 bind=op.get_bind();Base.metadata.create_all(bind)
 for name in ['video_daily_analytics','channel_daily_analytics','traffic_source_daily','geography_daily','device_daily','playlist_data','playlists','video_playlist_memberships','comments_summary','ingestion_jobs','derived_channel_features','analysis_results','experiments','discovered_channel_candidates','content_taxonomy']:
  op.execute(f'CREATE TABLE IF NOT EXISTS {name} (id SERIAL PRIMARY KEY, channel_id VARCHAR(64), video_id VARCHAR(32), recorded_on DATE, data JSONB NOT NULL DEFAULT \'{{}}\')')
def downgrade():Base.metadata.drop_all(op.get_bind())
