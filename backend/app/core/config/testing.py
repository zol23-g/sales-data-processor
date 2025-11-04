from .base import BaseSettings


class TestingSettings(BaseSettings):
    """Testing environment settings."""
    
    DEBUG: bool = True
    ENVIRONMENT: str = "testing"
    
    # Testing-specific overrides
    LOG_LEVEL: str = "DEBUG"
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]
    
    # File storage - use test directories
    UPLOAD_DIR: str = "test_uploads"
    OUTPUT_DIR: str = "test_outputs"
    
    # Redis - use different database
    REDIS_URL: str = "redis://localhost:6379/1"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # Security
    SECRET_KEY: str = "test-secret-key"
    
    model_config = {
        "env_file": ".env.testing",
        "extra": "ignore"
    }