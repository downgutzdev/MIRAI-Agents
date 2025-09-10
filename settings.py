from pydantic import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str | None = None
    REQUEST_TIMEOUT_SECONDS: float = 30.0
    ALLOW_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
