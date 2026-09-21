from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Media Authenticity Platform"
    DATABASE_URL: str = "mongodb://localhost:27017" # Default for local dev
    API_V1_STR: str = "/api"

    class Config:
        env_file = ".env"

settings = Settings()
