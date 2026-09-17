from pydantic_settings import BaseSettings
import os
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "JalJasoos Edge Gateway"
    SOCIETY_ID: str = os.getenv("EDGE_SOCIETY_ID", "society01")
    BUILDING_ID: str = os.getenv("EDGE_BUILDING_ID", "buildingA")

    # Database
    DATABASE_URL: str = os.getenv("EDGE_DATABASE_URL", "postgresql://jaljasoos:jaljasoos_pass@localhost:5433/jaljasoos_edge")

    # MQTT Broker (Local)
    MQTT_HOST: str = os.getenv("MQTT_BROKER_HOST", "localhost")
    MQTT_PORT: int = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    MQTT_USER: str = os.getenv("MQTT_USERNAME", "")
    MQTT_PASS: str = os.getenv("MQTT_PASSWORD", "")

    # Cloud Sync
    CLOUD_API_URL: str = os.getenv("CLOUD_API_URL", "http://localhost:8000")
    CLOUD_WS_URL: str = os.getenv("CLOUD_WS_URL", "ws://localhost:8000")
    EDGE_API_KEY: str = os.getenv("EDGE_API_KEY", "dev-edge-key-123")

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
