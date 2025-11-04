import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Application settings configuration."""
    
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
    SECRET_KEY: str = Field("your-secret-key-here", env="SECRET_KEY")
    TOKEN_EXPIRE_MINUTES: int = Field(30, env="TOKEN_EXPIRE_MINUTES")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(["http://localhost:3000"], env="ALLOWED_ORIGINS")
    
    # Pydantic v2 configuration
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


# Environment-specific settings
class DevelopmentSettings(Settings):
    DEBUG: bool = True
    ENVIRONMENT: str = "development"


class TestingSettings(Settings):
    DEBUG: bool = True
    ENVIRONMENT: str = "testing"
    REDIS_URL: str = "redis://localhost:6379/1"
    UPLOAD_DIR: str = "test_uploads"
    OUTPUT_DIR: str = "test_outputs"


class StagingSettings(Settings):
    DEBUG: bool = False
    ENVIRONMENT: str = "staging"


class ProductionSettings(Settings):
    DEBUG: bool = False
    ENVIRONMENT: str = "production"


def get_settings() -> Settings:
    """Get environment-specific settings."""
    env = os.getenv("ENVIRONMENT", "development")
    settings_map = {
        "development": DevelopmentSettings,
        "testing": TestingSettings,
        "staging": StagingSettings,
        "production": ProductionSettings,
    }
    return settings_map[env]()


settings = get_settings()