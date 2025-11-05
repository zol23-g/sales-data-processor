from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict, field_validator


class BaseSettings(BaseSettings):
    """Base application settings configuration."""
    
    # Application
    APP_NAME: str = "Sales Data Processor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # gRPC
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50051
    
    # HTTP
    HTTP_HOST: str = "0.0.0.0"
    HTTP_PORT: int = 8000
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS 
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database
    DATABASE_URL: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse ALLOWED_ORIGINS from string to list."""
        if isinstance(v, str):
            # Handle comma-separated string
            if ',' in v:
                return [origin.strip() for origin in v.split(',')]
            # Handle single value
            elif v:
                return [v.strip()]
            # Handle empty string
            else:
                return []
        return v
    
    # Pydantic v2 configuration
    model_config = ConfigDict(
        case_sensitive=True,
        extra="ignore",
        env_file_encoding='utf-8',
        env_prefix="",  # No prefix for environment variables
    )