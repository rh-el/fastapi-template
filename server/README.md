# Server

FastAPI backend application. See the root [README.md](../README.md) for full documentation.

## Database configuration (Supabase)

1. Copy `.env.example` to `.env`.
2. Replace `[YOUR-PASSWORD]` in `DATABASE_URL` with your Supabase database password.
3. Keep `?sslmode=require` in the connection string for Supabase.
4. Start the API and run migrations; both app runtime and Alembic read `DATABASE_URL`.
