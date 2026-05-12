.PHONY: install dev test seed migrate migration lint

install:
	python -m pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	python -m pytest -q

seed:
	python -c "from sqlmodel import Session; from app.core.db import engine, init_db; from app.services.seeder import seed_tours; init_db(); s=Session(engine); n=seed_tours(s); s.close(); print(f'seeded {n} tours')"

migrate:
	alembic upgrade head

migration:
	@if [ -z "$(name)" ]; then echo "usage: make migration name=add_field"; exit 1; fi
	alembic revision --autogenerate -m "$(name)"
