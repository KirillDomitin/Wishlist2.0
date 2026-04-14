CLAUDE.md

Project
This is a microservices-based application called Wishlist.

Purpose
This file defines strict development rules and conventions for AI agents (Claude Code) working on a Python microservices backend.

Tech Stack
- Python 3.12+
- FastAPI (async only)
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Redis
- Nginx (gateway / reverse proxy)
- Pydantic v2
- Docker & Docker Compose

Core Principles

1. Separation of Concerns
Routes must not contain business logic.
Business logic must be in services.
Database access must be in repositories.

Structure:
/api
/services
/repositories
/models
/schemas
/core

2. Async First
Always use async/await.
Avoid blocking operations.

3. Dependency Injection
Use FastAPI Depends.

4. Thin Controllers
Routes only validate, call service, return response.

5. Service Layer
Contains all business logic.

6. Repository Layer
Only database queries.

7. Pydantic
Use for all input/output. Do not expose ORM models.

8. Database
Use SQLAlchemy async and Alembic.

9. Redis
Use for caching and coordination.

10. Error Handling
Use custom exceptions and centralized handling.

Microservices Rules
Each service is independent.
Each has its own database.

Docker Rules
Each service has its own Dockerfile.
Use docker-compose for development.

Nginx
Acts as API Gateway.

Config
Use environment variables only.

Testing
Use pytest with async support.

Code Style
Type hints required.
Explicit over implicit.

Claude Code Best Practices

- Always follow structure
- Never put business logic in routes
- Always use async
- Always add type hints
- Separate layers strictly

When modifying code:
- Do not rewrite entire files unnecessarily
- Preserve architecture

Output rules:
- Production-ready code only
- No placeholders
- No pseudocode

Anti-Patterns

- Business logic in routes
- Sync DB calls
- Global mutable state
- Tight coupling
- Direct DB access from controllers

Flow
Request -> Router -> Service -> Repository -> DB

Dev Environment
Must run via docker-compose
Hot reload enabled

Production Deploy
Server: root@83.217.211.189, project at /opt/wishlist
Uses docker-compose (v1 CLI, not docker compose)

Deploy sequence:
  git fetch origin && git reset --hard origin/master
  docker-compose build <changed-services>
  docker-compose up -d

NEVER use git pull on the server — divergent branches cause silent no-op.
Always use git fetch + git reset --hard origin/master.

After nginx config changes always rebuild with --no-cache:
  docker-compose build --no-cache nginx

Summary
Think in layers
Think async
Think microservices
Keep code clean and scalable
