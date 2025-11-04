from .base import BaseSettings


class DevelopmentSettings(BaseSettings):
    """Development environment settings."""
    
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Development-specific overrides
    LOG_LEVEL: str = "DEBUG"
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File storage
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    model_config = {
        "env_file": ".env.development",
        "extra": "ignore"
    }