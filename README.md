# FastAPI + PostgreSQL Backend Template

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
```

## Database Migrations

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

## Environment Variables

| Variable                    | Description                    | Default |
|-----------------------------|--------------------------------|---------|
| `DATABASE_URL`              | PostgreSQL connection string   | —       |
| `JWT_SECRET_KEY`            | Secret key for JWT signing     | —       |
| `JWT_ALGORITHM`             | JWT algorithm                  | HS256   |
| `JWT_ACCESS_TOKEN_EXPIRE_DAYS` | Token expiration in days    | 2       |

## Docker Environments

| File                    | Purpose     | Backend Port | DB Port |
|-------------------------|-------------|-------------|---------|
| `docker-compose.dev.yml`  | Development | 8000        | 5432    |
| `docker-compose.prod.yml` | Production  | 8000        | 5432    |
| `docker-compose.test.yml` | Testing     | 8001        | 5433    |
