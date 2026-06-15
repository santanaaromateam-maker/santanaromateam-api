from datetime import datetime, timezone

from app.auth_utils import hash_password
from app.config import settings
from app.database import admins_collection, connect_db


def init_db() -> None:
    connect_db()
    _seed_admin()


def _seed_admin() -> None:
    email = settings.admin_email.lower()
    if admins_collection().find_one({"email": email}):
        return

    admins_collection().insert_one(
        {
            "email": email,
            "hashed_password": hash_password(settings.admin_password),
            "created_at": datetime.now(timezone.utc),
        }
    )
