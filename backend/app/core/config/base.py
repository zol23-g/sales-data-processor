from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict, field_validator


class BaseSettings(BaseSettings):
    """Base application settings configuration."""
    
    # Application
    APP_NAME: str = "Sales Data Processor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(False, env="DEBUG")
    
    # Environment
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    
    # gRPC
    GRPC_HOST: str = Field("0.0.0.0", env="GRPC_HOST")
    GRPC_PORT: int = Field(50051, env="GRPC_PORT")
    
    # HTTP
    HTTP_HOST: str = Field("0.0.0.0", env="HTTP_HOST")
    HTTP_PORT: int = Field(8000, env="HTTP_PORT")
    
    # File Storage
    UPLOAD_DIR: str = Field("uploads", env="UPLOAD_DIR")
    OUTPUT_DIR: str = Field("outputs", env="OUTPUT_DIR")
    MAX_FILE_SIZE: int = Field(100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB
    
    # Redis
    REDIS_URL: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # Celery
    CELERY_BROKER_URL: str = Field("redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field("redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # Security
    SECRET_KEY: str = Field("your-secret-key-change-in-production", env="SECRET_KEY")
    TOKEN_EXPIRE_MINUTES: int = Field(30, env="TOKEN_EXPIRE_MINUTES")
    
    # CORS 
    ALLOWED_ORIGINS: List[str] = Field(["http://localhost:3000"], env="ALLOWED_ORIGINS")
    
    # Database (if needed later)
    DATABASE_URL: str = Field("", env="DATABASE_URL")
    
    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    
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
        env_file_encoding='utf-8'
    )