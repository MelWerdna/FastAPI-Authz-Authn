import aiosqlite
from pathlib import Path
from src.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent


def _db_path() -> str:
    path = Path(settings.DATABASE_URL)
    if not path.is_absolute():
        return str(BASE_DIR / path)
    return str(path)


async def init_db() -> None:
    async with aiosqlite.connect(_db_path()) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                email         TEXT    UNIQUE NOT NULL,
                username      TEXT    NOT NULL,
                password      TEXT    NOT NULL,
                is_active     INTEGER NOT NULL DEFAULT 0,
                is_deleted    INTEGER NOT NULL DEFAULT 0,
                token_version INTEGER NOT NULL DEFAULT 0,
                role          TEXT    NOT NULL DEFAULT 'user'
            )
        """)
        await db.commit()


async def get_db():
    async with aiosqlite.connect(_db_path()) as db:
        db.row_factory = aiosqlite.Row
        yield db
