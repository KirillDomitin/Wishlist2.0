from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    APP_BASE_URL: str = "https://wl.404.mn"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
