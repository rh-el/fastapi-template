# FastAPI + PostgreSQL Backend Template

backend template built with **FastAPI**, **PostgreSQL**, **SQLModel**, and **Alembic**.

## Stack

- **FastAPI** — async web framework
- **SQLModel** — SQLAlchemy + Pydantic integration
- **PostgreSQL** — relational database
- **Alembic** — database migrations
- **JWT** — authentication via cookies + bearer tokens
- **Argon2** — password hashing
- **Docker** — containerized development and deployment

## Quick Start

### With Docker (recommended)

```bash
# Start development environment
chmod +x start-dev.sh
./start-dev.sh

# Run database migrations
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head
```

### Without Docker

```bash
cd server

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (copy and edit .env.example)
cp ../.env.example .env

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```       | Yes  |

## Database Migrations

```bash
# Create a new migration after model changes
docker-compose -f docker-compose.dev.yml exec backend alembic revision --autogenerate -m "description of changes"

# Apply migrations
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

# Rollback one step
docker-compose -f docker-compose.dev.yml exec backend alembic downgrade -1
```
