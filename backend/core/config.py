import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Backend runtime
    forge_port: int = 8765
    forge_data_dir: str = os.environ.get("FORGE_DATA_DIR", "./data")

    # Database
    forge_db_mode: str = "sqlite"  # sqlite | postgres
    database_url: str = ""  # computed in model_post_init

    # ChromaDB
    forge_chroma_mode: str = "embedded"  # embedded | server
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    # LiveKit
    livekit_url: str = ""
    livekit_api_key: str = ""
    livekit_api_secret: str = ""

    # LLM / STT / TTS keys
    anthropic_api_key: str = ""
    deepgram_api_key: str = ""
    cartesia_api_key: str = ""

    # App
    app_version: str = "1.0.0"

    def model_post_init(self, __context: object) -> None:
        if not self.database_url:
            db_path = Path(self.forge_data_dir) / "forge_chamber.db"
            self.database_url = f"sqlite+aiosqlite:///{db_path}"


settings = Settings()
