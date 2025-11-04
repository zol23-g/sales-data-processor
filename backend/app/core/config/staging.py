from .base import BaseSettings


class StagingSettings(BaseSettings):
    """Staging environment settings."""
    
    DEBUG: bool = False
    ENVIRONMENT: str = "staging"
    
    # Staging-specific overrides
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: list = [
        "https://staging.domain.com",
        "http://staging.domain.com"
    ]
    
    # File storage
    UPLOAD_DIR: str = "/app/uploads"
    OUTPUT_DIR: str = "/app/outputs"
    
    # Redis - use service names for Docker
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    model_config = {
        "env_file": ".env.staging",
        "extra": "ignore"
    }