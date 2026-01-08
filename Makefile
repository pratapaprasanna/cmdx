.PHONY: install test run migrate dev clean

install:
	pip install -r requirements.txt

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html

run:
	uvicorn main:app --reload

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(msg)"

dev: install migrate run

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

