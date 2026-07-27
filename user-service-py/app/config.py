"""
Podešavanja aplikacije - čita se iz .env fajla.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Baza podataka (User servis ima svoju bazu)
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_DATABASE: str = "users_db"
    DB_USERNAME: str = "root"
    DB_PASSWORD: str = ""

    # JWT podešavanja
    SECRET_KEY: str = "promeni-ovaj-tajni-kljuc-u-produkciji"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
        )


settings = Settings()
