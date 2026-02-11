"""Centralized configuration using pydantic-settings."""

from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Space-Track.org
    spacetrack_username: str = Field(default="", alias="SPACETRACK_USERNAME")
    spacetrack_password: str = Field(default="", alias="SPACETRACK_PASSWORD")

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # Database
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'satellites.db'}"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True

    # Streamlit
    streamlit_port: int = 8501

    # Logging
    log_level: str = "INFO"
    log_dir: str = str(BASE_DIR / "logs")

    # Collision detection
    collision_threshold_km: float = 10.0
    analysis_window_hours: int = 24
    propagation_step_minutes: int = 1

    # Ground station
    ground_station_lat: float = 28.5721
    ground_station_lon: float = -80.6480
    ground_station_elevation_m: float = 3.0
    ground_station_name: str = "Kennedy Space Center"

    # Cache TTL
    tle_cache_ttl: int = 3600
    analysis_cache_ttl: int = 1800

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def db_path(self) -> Path:
        url = self.database_url
        if url.startswith("sqlite:///"):
            return Path(url.replace("sqlite:///", ""))
        return BASE_DIR / "data" / "satellites.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
