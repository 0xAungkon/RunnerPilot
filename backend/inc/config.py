from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///test.db"
    ADMIN_EMAIL: str = "admin@gmail.com"
    ADMIN_PASSWORD: str = "admin123"
    SECRET_KEY: str = "changeme"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    ENVIRONMENT: str = "production"
    VOLUME_PATH: str = "/volume"
    RELEASE_CACHE_TTL_HOURS: int = 72

    class Config:
        env_file = ".env"

settings = Settings()


def is_dev() -> bool:
    """Check if the application is running in development environment."""
    return settings.ENVIRONMENT.lower() == "development"
