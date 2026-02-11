# FastAPI + PostgreSQL Backend Template

A minimal, production-ready backend template built with **FastAPI**, **PostgreSQL**, **SQLModel**, and **Alembic**.

## Architecture

```
server/app/
├── main.py              # FastAPI application entry point
├── db.py                # Database engine and session management
├── core/
│   ├── config.py        # Application settings (env-based)
│   ├── dependencies.py  # Dependency injection (auth, services)
│   ├── exceptions.py    # Custom exception classes
│   ├── exception_handlers.py  # Global exception handlers
│   └── security.py      # OAuth2 scheme configuration
├── models/
│   ├── __init__.py      # SQLModel table definitions (User, Vote)
│   ├── user.py          # User Pydantic schemas
│   ├── vote.py          # Vote Pydantic schemas
│   └── token.py         # JWT token schemas
├── crud/
│   ├── user_crud.py     # User database operations
│   └── vote_crud.py     # Vote database operations
├── services/
│   ├── user_service.py  # User business logic + auth
│   └── vote_service.py  # Vote business logic
├── routes/
│   ├── user.py          # User API endpoints
│   └── vote.py          # Vote API endpoints
└── migrations/          # Alembic migration scripts
```

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

## API Endpoints

### Users (`/api/v1/user`)
| Method | Endpoint   | Description          | Auth |
|--------|-----------|----------------------|------|
| POST   | /signup   | Register new user    | No   |
| POST   | /token    | Login (get JWT)      | No   |
| GET    | /         | List all users       | No   |
| GET    | /me       | Get current user     | Yes  |
| PUT    | /         | Update current user  | Yes  |
| DELETE | /delete   | Delete current user  | Yes  |
| POST   | /logout   | Clear auth cookie    | No   |

### Votes (`/api/v1/vote`)
| Method | Endpoint    | Description           | Auth |
|--------|------------|-----------------------|------|
| GET    | /          | List all votes        | No   |
| GET    | /user/me   | List my votes         | Yes  |
| GET    | /{vote_id} | Get vote by ID        | No   |
| POST   | /          | Create a vote         | Yes  |
| PUT    | /{vote_id} | Update a vote         | Yes  |
| DELETE | /{vote_id} | Delete a vote         | Yes  |

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
