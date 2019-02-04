import os
from typing import Optional

from dotenv import load_dotenv


def init() -> None:
    load_dotenv()


def get(key: str) -> Optional[str]:
    return os.getenv(key)


# Shortcut variables for Framework.
PIPELINE_DATABASE_URL = get('PIPELINE_DATABASE_URL')
