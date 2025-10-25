# RunnerPilot Docker Compose Helper

.PHONY: help build up down logs frontend-logs backend-logs clean rebuild

help:
	@echo "RunnerPilot Docker Compose Commands"
	@echo "===================================="
	@echo "make build          - Build all services"
	@echo "make up             - Start all services"
	@echo "make down           - Stop all services"
	@echo "make logs           - Show logs from all services"
	@echo "make frontend-logs  - Show frontend logs only"
	@echo "make backend-logs   - Show backend logs only"
	@echo "make clean          - Remove all containers and volumes"
	@echo "make rebuild        - Rebuild and start all services"
	@echo "make ps             - Show running containers"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

frontend-logs:
	docker-compose logs -f frontend

backend-logs:
	docker-compose logs -f backend

clean:
	docker-compose down -v
	docker image prune -f

rebuild: clean build up
	@echo "Services rebuilt and started!"
	@echo "Frontend: http://localhost"
	@echo "Backend API: http://localhost:8000"

ps:
	docker-compose ps

shell-frontend:
	docker-compose exec frontend /bin/sh

shell-backend:
	docker-compose exec backend /bin/bash
