ifneq ("$(wildcard .env)","")
	include .env
	export
endif

PYTHON := .venv/bin/python3
SCRIPTS_DIR := scripts

LINT_EXCLUDES=.venv
LINT_IGNORE=E501,F841
LINT_PER_FILE_IGNORES=\
	*:F401

all:
	echo $(PYTHON)

.PHONY: install run migrate makemigrations shell test clean

setup:

	@if [ ! -f .env ]; then \
		cp .env.example .env && \
		echo "✓ .env file setuped"; \
	else \
		echo "✓ .env file already exists, skipping copy"; \
	fi

	@if [ ! -d .venv ]; then \
		python3 -m venv .venv && \
		echo "✓ Virtual environment created"; \
	else \
		echo "✓ Virtual environment already exists, skipping creation"; \
	fi
	$(PYTHON) -m pip install uv
	$(PYTHON) -m uv sync
	
devInfra:
	docker compose -f pipeline/dev-infra/postgresql/compose.yml up -d
	docker compose -f pipeline/dev-infra/redis/compose.yml up -d
	docker compose -f pipeline/dev-infra/pgadmin/compose.yml up -d

cleanInfra:
	docker compose -f pipeline/dev-infra/postgresql/compose.yml down
	docker compose -f pipeline/dev-infra/redis/compose.yml down
	docker compose -f pipeline/dev-infra/pgadmin/compose.yml down
	sudo rm -rf  ~/.volumn/emp_service
	make dev-up

run:
	$(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTHON) -m pytest -v 
migrate:
	@read -p "Do you want to stamp your database? (y/n): " choice; \
	if [ "$$choice" = "y" ]; then \
		$(PYTHON) -m alembic stamp head; \
	fi
	$(PYTHON) -m alembic revision --autogenerate -m "$(or $(MSG), 'Auto migration')"
	$(PYTHON) -m alembic upgrade head


clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -path "./*" -not -path "./.venv/*" -not -path "./venv/*" -path "*/migrations/*.py" -not -name "__init__.py" -delete

lint:
	$(PYTHON) -m flake8 . \
		--exclude=$(LINT_EXCLUDES) \
		--ignore=$(LINT_IGNORE) \
		--per-file-ignores="$(LINT_PER_FILE_IGNORES)" || true
format:
	$(PYTHON) -m autoflake --remove-all-unused-imports --ignore-init-module-imports --expand-star-imports --in-place --recursive .  --exclude=.venv 
	$(PYTHON) -m black --exclude '.venv' .

prepare:
	@echo "preparing for linting....."
	make lint

load-data:
	$(PYTHON) ./scripts/initialdb-loader.py --default-file --tenant-id de104504-d40f-4a45-bf7c-c1c5ed7d103e

%:
	@if [ -f $(SCRIPTS_DIR)/$@.py ]; then \
		$(PYTHON) $(SCRIPTS_DIR)/$@.py $(filter-out $@,$(MAKECMDGOALS)); \
	elif [ -f $(SCRIPTS_DIR)/$@.sh ]; then \
		bash $(SCRIPTS_DIR)/$@.sh $(filter-out $@,$(MAKECMDGOALS)); \
	else \
		echo "No rule or script found for '$@'"; \
		exit 1; \
	fi
