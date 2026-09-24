from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NOTES_")

    database_url: str = f"sqlite:///{BASE_DIR / 'notes.db'}"
    uploads_dir: Path = BASE_DIR / "uploads"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    refresh_token_expire_days: int = 14
    max_upload_size_bytes: int = 10 * 1024 * 1024


settings = Settings()
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
