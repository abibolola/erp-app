from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    COOKIE_SECURE: bool = False  # Set False for development and True for Production
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: str = "example.com"  # Set to your domain in production
    COOKIE_HTTPONLY: bool = True
    CSRF_SECRET_KEY: str  # Add this to .env
    ENV: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
