from datetime import datetime, timezone

from app.cloudinary_service import WIDTH_HERO, optimize_image_url
from app.database import site_settings_collection
from app.schemas import SiteSettingsAdmin, SiteSettingsPublic

SETTINGS_ID = "global"
DEFAULT_TEAM_PHOTO_ALT = "Santana Aroma Cleaning team"


def _empty_doc() -> dict:
    return {
        "_id": SETTINGS_ID,
        "team_photo_url": "",
        "team_photo_alt": DEFAULT_TEAM_PHOTO_ALT,
        "team_photo_public_id": "",
    }


def get_site_settings_doc() -> dict:
    doc = site_settings_collection().find_one({"_id": SETTINGS_ID})
    if not doc:
        return _empty_doc()
    return doc


def site_settings_to_public(doc: dict | None = None) -> SiteSettingsPublic:
    data = doc or get_site_settings_doc()
    url = (data.get("team_photo_url") or "").strip()
    return SiteSettingsPublic(
        teamPhotoUrl=optimize_image_url(url, width=WIDTH_HERO) if url else "",
        teamPhotoAlt=(data.get("team_photo_alt") or DEFAULT_TEAM_PHOTO_ALT).strip(),
    )


def site_settings_to_admin(doc: dict | None = None) -> SiteSettingsAdmin:
    data = doc or get_site_settings_doc()
    return SiteSettingsAdmin(
        teamPhotoUrl=(data.get("team_photo_url") or "").strip(),
        teamPhotoAlt=(data.get("team_photo_alt") or DEFAULT_TEAM_PHOTO_ALT).strip(),
        teamPhotoPublicId=(data.get("team_photo_public_id") or "").strip(),
        updatedAt=data.get("updated_at"),
    )


def update_site_settings(*, team_photo_url: str, team_photo_alt: str, team_photo_public_id: str = "") -> dict:
    now = datetime.now(timezone.utc)
    payload = {
        "team_photo_url": team_photo_url.strip(),
        "team_photo_alt": (team_photo_alt.strip() or DEFAULT_TEAM_PHOTO_ALT),
        "team_photo_public_id": team_photo_public_id.strip(),
        "updated_at": now,
    }
    site_settings_collection().update_one(
        {"_id": SETTINGS_ID},
        {"$set": payload, "$setOnInsert": {"_id": SETTINGS_ID}},
        upsert=True,
    )
    return get_site_settings_doc()
