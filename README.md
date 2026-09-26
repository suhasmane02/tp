# Local YouTube Vlog Analytics

A local-first Docker application for a Marathi/Maharashtra family-vlog channel. It uses the official YouTube Data API for public data, OAuth for the owner, and preserves snapshot history. It **does not scrape YouTube** or claim access to YouTube's recommendation algorithm.

## One-click start on Windows
1. Install and start [Docker Desktop](https://www.docker.com/products/docker-desktop/) once. Git, Python, PostgreSQL, and Node do **not** need to be installed.
2. Download/clone this project, then double-click **`install.bat`**. The installer verifies Docker, creates a local `.env` with a random application secret, builds the containers, waits for `/ready`, and opens http://localhost:8000.
3. On the first screen, click **Load demo data** to use the whole dashboard immediately without Google credentials. Add Google credentials to `.env` later to synchronize live channels.

The installer is idempotent: double-click it again after upgrades. `start.bat` starts an existing installation, `stop.bat` stops it, `restart.bat` restarts it, and `logs.bat` shows diagnosis logs. If Docker Desktop is not installed/running, the installer gives the exact next step instead of partially installing anything.

Linux/macOS: `cp .env.example .env && docker compose up -d --build`. Check services with `docker compose ps`; logs are `docker compose logs -f app`.

## Google Cloud setup
Create a Google Cloud project, enable **YouTube Data API v3**, **YouTube Analytics API**, and optionally **YouTube Reporting API**. Create a Desktop/Web OAuth client, add `http://localhost:8000/api/oauth/callback` as an authorized redirect URI, then place its client ID/secret only in `.env`. Create a restricted Data API key and place it in `YOUTUBE_API_KEY`. Never commit `.env`, OAuth tokens, client secrets, or backups.

## What is collected
| Metric | Source | Own | Competitor | History | Refresh |
|---|---|---:|---:|---:|---|
| Channel/video public counts, metadata, uploads | YouTube Data API v3 (`channels.list`, `playlistItems.list`, `videos.list`) | Yes | Yes | snapshots | adaptive/public cron |
| Watch time, average duration/percentage, shares, subscribers, traffic/geography/device | YouTube Analytics `reports.query` with `yt-analytics.readonly` | Yes, when API reports it | No | daily aggregates | analytics cron |
| Impressions/CTR/retention/new/returning viewers | Analytics API only where its documented report supports the requested metric/dimensions | Conditional | No | conditional | analytics cron |
| Local Performance Index | Derived locally | Yes | public inputs only | recomputed | daily |

Unavailable metrics are shown as unavailable rather than guessed. Public API does not reliably expose a Shorts flag; the classifier only labels a Short when public evidence is conservative (duration plus `#Shorts`), and records its reason/confidence. The Local Performance Index is an internal analytical model — **not a YouTube ranking score**.

## Operations
- `docker compose exec app python -m app.cli add-channel CHANNEL_URL`
- `docker compose exec app python -m app.cli add-channel CHANNEL_URL --competitor`
- `docker compose exec app python -m app.cli sync`
- `docker compose exec app python -m app.cli export --channel CHANNEL_ID --format csv`
- `backup.bat`; restore with `restore.bat backups\youtube_analytics.sql`.

The in-process scheduler runs public discovery/snapshot sync from `PUBLIC_SYNC_CRON`; its jobs are idempotent through primary keys and snapshot uniqueness. Data is stored in PostgreSQL volume `postgres_data`; raw archival directory is mounted at `data/`.

## API / pages
`/health`, `/ready`, `/api/system/status`, `/api/channels`, `/api/videos/{id}`, `/api/alerts`, `/api/analytics/*`, `/api/competitors`; dashboard routes include `/dashboard`, `/channels`, `/videos`, `/competitors`, `/shorts`, `/long-form`, `/alerts`, and `/settings`.

## Development and troubleshooting
Run `pytest`. Tests use no live API. If a sync fails, inspect `/api/alerts` and `docker compose logs app`; quota/API errors are retained as ingestion failures. Check redirect URI exactly matches `.env`; public competitors never expose private Analytics data. PostgreSQL migrations are under `migrations/versions`. The schema includes normalized channels, videos, snapshots, derived features, alerts, quota/request records, OAuth metadata, and supplemental daily analytics/taxonomy/experiment tables.
