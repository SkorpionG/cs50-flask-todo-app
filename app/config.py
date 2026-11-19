import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "database.db"
SQL_DIR = BASE_DIR / "sql"
SCHEMAS_DIR = SQL_DIR / "schemas"
INDEX_FILE = SQL_DIR / "index.sql"
DROP_TABLES_FILE = SQL_DIR / "drop_tables.sql"

load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""

    # In production, set a persistent SECRET_KEY via environment variable
    SECRET_KEY: str | bytes = os.environ.get("SECRET_KEY") or os.urandom(24)
    SESSION_TYPE: str = "filesystem"
    SESSION_PERMANENT: bool = True
    DATABASE_PATH: Path = DATABASE_PATH
