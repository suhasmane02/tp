up:
	docker compose up -d --build
down:
	docker compose down
test:
	docker compose run --rm app pytest -q
logs:
	docker compose logs -f app
seed:
	docker compose exec app python -m app.cli seed-demo
backup:
	docker compose exec -T postgres pg_dump -U youtube youtube_analytics > backups/youtube_analytics.sql
