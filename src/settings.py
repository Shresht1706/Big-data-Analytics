from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings

DOTENV = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings, extra="allow"):
    # Postgres
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    PG_PORT: int
    PG_HOST: str
    PG_DSN: str = ""

    # Parser
    TW_LOGIN: str
    TW_PASSWORD: str
    TW_USERNAME: str

    @model_validator(mode="after")  # type: ignore
    def setup_pg_dsn(self) -> None:
        self.PG_DSN: str = (  # pylint: disable=invalid-name
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            + f"{self.PG_HOST}:{self.PG_PORT}/{self.POSTGRES_DB}"
        )


settings: Settings = Settings(_env_file=DOTENV)
