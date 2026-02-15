"""Configuration management using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Racing API
    racing_api_username: str = ""
    racing_api_password: str = ""
    racing_api_base_url: str = "https://api.theracingapi.com/v1/north-america"

    # Database
    database_url: str = "postgresql://racing_user:racing_dev_password@localhost:5433/racing_db"
    db_host: str = "localhost"
    db_port: int = 5433
    db_name: str = "racing_db"
    db_user: str = "racing_user"
    db_password: str = "racing_dev_password"

    # Rate Limiting
    rate_limit_requests: int = 2
    rate_limit_period: float = 1.5

    # Paths
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = project_root / "data-ingestion" / "data"
    raw_data_dir: Path = data_dir / "raw"
    processed_data_dir: Path = data_dir / "processed"
    logs_dir: Path = project_root / "data-ingestion" / "logs"

    @property
    def DATABASE_URL(self) -> str:
        """Get database URL for SQLAlchemy."""
        return self.database_url

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.raw_data_dir.mkdir(parents=True, exist_ok=True)
settings.processed_data_dir.mkdir(parents=True, exist_ok=True)
settings.logs_dir.mkdir(parents=True, exist_ok=True)