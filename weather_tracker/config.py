from os import environ

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class RedisConfig(BaseModel):
    host: str = Field(validation_alias="REDIS_HOST")
    port: int = Field(validation_alias="REDIS_PORT")
    session_lifetime: int = Field(validation_alias="REDIS_SESSION_LIFETIME_SEC")


class PostgresConfig(BaseModel):
    user: str = Field(validation_alias="POSTGRES_USER")
    password: str = Field(validation_alias="POSTGRES_PASSWORD")
    db: str = Field(validation_alias="POSTGRES_DB")
    host: str = Field(validation_alias="POSTGRES_HOST")
    port: str = Field(validation_alias="POSTGRES_PORT")

    @property
    def pg_async_url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class OpenWeatherConfig(BaseModel):
    api_key: str = Field(validation_alias="OPENWEATHER_API_KEY")
    search_url: str = Field(validation_alias="OPENWEATHER_SEARCH_URL")
    weather_url: str = Field(validation_alias="OPENWEATHER_WEATHER_URL")


class Config(BaseModel):
    open_weather: OpenWeatherConfig
    postgres: PostgresConfig
    redis: RedisConfig

    @classmethod
    def from_env(cls, env_path: str = ".env"):
        load_dotenv(env_path, override=True)
        return cls(
            open_weather=OpenWeatherConfig(**environ), postgres=PostgresConfig(**environ), redis=RedisConfig(**environ)
        )
