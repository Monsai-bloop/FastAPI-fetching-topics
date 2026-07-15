import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any
# Dynamically finds the root directory containing your .env file
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")

class Settings(BaseSettings):
	API_KEY: str
	REDIS_HOST: str
	REDIS_PORT: int
	REDIS_DB: int
	CURRENT_URL: str

	model_config = SettingsConfigDict(env_file=env_path, env_file_encoding="utf-8")


settings = Settings()

