"""Application settings using Pydantic Settings."""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # GCP Configuration
    gcp_project_id: str
    gcp_region: str = "us-central1"
    gcp_service_account_key_path: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # Vertex AI
    vertex_ai_model: str = "gemini-2.5-pro"
    vertex_ai_temperature: float = 0.3
    vertex_ai_max_tokens: int = 16384
    
    # Firebase
    firebase_database_url: Optional[str] = None
    
    # Sentry
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "development"
    
    # Rate Limiting
    rate_limit_max_requests: int = 10
    rate_limit_window_seconds: int = 60
    
    # Feature Flags
    enable_caching: bool = True
    enable_ab_testing: bool = False
    cache_ttl_seconds: int = 86400  # 24 hours
    
    # Monitoring
    log_level: str = "INFO"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.sentry_environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.sentry_environment == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
