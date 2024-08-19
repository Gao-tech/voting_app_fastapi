from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Explicitly load the .env file
load_dotenv()

# Pydantic Settings provide optional features for loading a settings or config class from environment var/secrets files

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()