from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from app.config import settings

_client: MongoClient | None = None
_db: Database | None = None


def connect_db() -> Database:
    global _client, _db
    if _db is None:
        _client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
        _client.admin.command("ping")
        _db = _client[settings.mongodb_db_name]
        _ensure_indexes(_db)
    return _db


def close_db() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
    _client = None
    _db = None


def get_db() -> Database:
    if _db is None:
        return connect_db()
    return _db


def admins_collection() -> Collection:
    return get_db()["admins"]


def services_collection() -> Collection:
    return get_db()["services"]


def site_settings_collection() -> Collection:
    return get_db()["site_settings"]


def _ensure_indexes(db: Database) -> None:
    db["admins"].create_index("email", unique=True)
    db["services"].create_index("slug", unique=True)
    db["services"].create_index([("order", ASCENDING), ("_id", ASCENDING)])
