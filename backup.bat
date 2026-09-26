@echo off
if not exist backups mkdir backups
docker compose exec -T postgres pg_dump -U youtube youtube_analytics > backups\youtube_analytics.sql
