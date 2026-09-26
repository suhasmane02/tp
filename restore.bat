@echo off
if "%1"=="" echo Usage: restore.bat backups\youtube_analytics.sql & exit /b 1
type %1 | docker compose exec -T postgres psql -U youtube youtube_analytics
