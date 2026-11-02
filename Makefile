export TAILWINDCSS_VERSION := v3.4.17

.PHONY: dev runserver tailwind-watch css css-prod vendors migrate collectstatic download-vendors

dev:
	$(MAKE) -j2 runserver tailwind-watch

runserver:
	uv run python manage.py runserver

tailwind-watch:
	uv run tailwindcss -i ./static/src/input.css -o ./static/css/output.css --watch

css:
	uv run tailwindcss -i ./static/src/input.css -o ./static/css/output.css

css-prod:
	uv run tailwindcss -i ./static/src/input.css -o ./static/css/output.css --minify

vendors download-vendors:
	uv run python download_vendors.py

migrate:
	uv run python manage.py migrate

collectstatic:
	uv run python manage.py collectstatic --noinput
