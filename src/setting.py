from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    celery_broker_url: str
    celery_result_backend: str
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
