from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "LLM API"
    openai_api_key: str | None = None
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_server: str | None = None
    postgres_port: str | None = None
    postgres_db: str | None = None
    embeddings_model_name: str | None = None
    similarity_threshold: float = 0.9
    chunk_size: int = 500
    chunk_overlap: int = 50

    class Config:
        env_file = ".env"