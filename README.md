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

## CTV Interactive Advertising

This project includes a real-time interactive advertising system that connects CTVs (Connected TVs) with smartphones through WebSockets and REST APIs.

**How it works:** An ad creative (HTML/JS) running on a CTV webview registers a session when the viewer presses a remote button. The viewer's phone pairs via a short code, then phone interactions are relayed to the CTV in real time.

- Full integration guide: [server/docs/CTV_INTEGRATION.md](server/docs/CTV_INTEGRATION.md)
- API docs (Swagger): `http://localhost:8000/docs` (when running)
