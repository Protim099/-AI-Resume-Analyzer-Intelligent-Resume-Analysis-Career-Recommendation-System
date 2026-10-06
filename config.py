from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/resume_analyzer"
    SECRET_KEY: str = "change-this-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_MB: int = 5
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "Admin@12345"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    USE_EMBEDDINGS: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
