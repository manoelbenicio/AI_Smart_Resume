DC := $(shell if command -v docker-compose >/dev/null 2>&1; then echo docker-compose; else echo "docker compose"; fi)

.PHONY: up down build test logs shell health clean

up:
	$(DC) up -d

down:
	$(DC) down

build:
	$(DC) up -d --build

test:
	$(DC) exec -T smart-resume-api pytest tests/ -v

logs:
	$(DC) logs -f smart-resume-api

shell:
	$(DC) exec smart-resume-api /bin/sh

health:
	curl -fsS http://localhost:8001/api/v1/health

clean:
	$(DC) down -v --remove-orphans
