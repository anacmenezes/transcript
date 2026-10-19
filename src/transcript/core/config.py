
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    temp_dir: Path = PROJECT_ROOT / "temp"

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY não configurada. "
                "Verifique o arquivo .env."
            )

        return cls(openai_api_key=api_key)


def get_settings() -> Settings:
    return Settings.from_env()