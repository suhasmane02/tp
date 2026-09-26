#!/usr/bin/env sh
set -eu
mkdir -p "${BACKUP_DIR:-backups}"
docker compose exec -T postgres pg_dump -U "${POSTGRES_USER:-youtube}" "${POSTGRES_DB:-youtube_analytics}" > "${BACKUP_DIR:-backups}/youtube_analytics-$(date +%F).sql"
