# For: Central system configuration and default verification thresholds
# Must never: Hardcode production credentials or bypass security defaults

import os
from pathlib import Path
from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "ADVS Engine"
    version: str = "1.0.0"
    host: str = "127.0.0.1"
    port: int = int(os.environ.get("ADVS_ENGINE_PORT", "8000"))
    jwt_secret: str = os.environ.get("ADVS_JWT_SECRET", "advs-drdo-rac-secure-key-2026-production-grade")
    launch_token: str = os.environ.get("ADVS_LAUNCH_TOKEN", "advs-dev-local-token")
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    base_dir: Path = Path(os.environ.get("ADVS_BASE_DIR", str(Path(__file__).resolve().parent.parent.parent)))
    data_dir: Path = Path(os.environ.get("ADVS_DATA_DIR", str(base_dir / "data")))
    storage_dir: Path = Path(os.environ.get("ADVS_STORAGE_DIR", str(data_dir / "encrypted_storage")))
    db_path: Path = Path(os.environ.get("ADVS_DB_PATH", str(data_dir / "advs.db")))
    
    # Verification and Quality Thresholds
    confidence_threshold_default: float = 0.97
    auto_accept_threshold: float = 0.97
    name_match_high: float = 90.0
    name_match_medium: float = 75.0
    percentage_tolerance: float = 0.01
    quality_blur_min_variance: float = 100.0
    quality_min_resolution: int = 300
    manual_minutes_per_doc: int = 4
    enabled_languages: list[str] = Field(default_factory=lambda: ["en", "hi"])

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.storage_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
