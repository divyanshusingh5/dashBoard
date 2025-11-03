from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "StyleLeap Claims Analytics API"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://localhost:5179",
        "http://localhost:3000",
        "http://localhost:8080"
    ]
    DEBUG: bool = True

    # Data paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: str = str(BASE_DIR.parent / "frontend" / "public")
    CSV_FILE_PATH: str = str(BASE_DIR.parent / "frontend" / "public" / "dat.csv")
    AGGREGATED_DATA_DIR: str = str(BASE_DIR.parent / "frontend" / "public")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
