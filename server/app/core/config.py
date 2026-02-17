import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Template"
    PROJECT_DESCRIPTION: str = "A production-ready FastAPI backend template with PostgreSQL"
    PROJECT_VERSION: str = "0.1.0"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_PUBLISHABLE_KEY: str = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")

    BACKEND_CORS_ORIGINS: list = ["https://statics.dmcdn.net", "https://localhost:8080", "*"]

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_DAYS", "2"))


settings = Settings()
