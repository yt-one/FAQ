import os

from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str


def load_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "mysql+aiomysql://root:159874@localhost:3306/faq")
    )


settings = load_settings()
