from pydantic import Field
from .base import BaseSettings


class ProductionSettings(BaseSettings):
    """Production environment settings."""
    
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Production-specific overrides
    LOG_LEVEL: str = "WARNING"
    ALLOWED_ORIGINS: list = [
        "https://domain.com",
        "https://www.domain.com"
    ]
    
    # File storage
    UPLOAD_DIR: str = "/app/uploads"
    OUTPUT_DIR: str = "/app/outputs"
    
    # Redis - use service names for Docker
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # Security - should be set via environment variables
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    
    model_config = {
        "env_file": ".env.production",
        "extra": "ignore"
    }