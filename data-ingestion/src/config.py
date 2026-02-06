"""Configuration management using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Racing API
    racing_api_username: str
    racing_api_password: str
    racing_api_base_url: str = "https://api.theracingapi.com/v1/north-america"

    # Rate Limiting
    rate_limit_requests: int = 2
    rate_limit_period: float = 1.5  # More conservative default

    # Paths
    project_root: Path = Path(__file__).parent.parent.parent  # Go up to horse-racing-ai/
    data_dir: Path = project_root / "data-ingestion" / "data"
    raw_data_dir: Path = data_dir / "raw"
    processed_data_dir: Path = data_dir / "processed"
    logs_dir: Path = project_root / "data-ingestion" / "logs"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'  # Ignore extra fields in .env
    )


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.raw_data_dir.mkdir(parents=True, exist_ok=True)
settings.processed_data_dir.mkdir(parents=True, exist_ok=True)
settings.logs_dir.mkdir(parents=True, exist_ok=True)