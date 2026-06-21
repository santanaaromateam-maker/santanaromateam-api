import re

import cloudinary
import cloudinary.uploader

from app.config import settings

# Delivery widths (public web)
WIDTH_CARD = 640
WIDTH_GALLERY = 900
WIDTH_HERO = 1200

# Max stored master after upload
UPLOAD_MAX_EDGE = 2000

_CLOUDINARY_HOST = re.compile(r"^https?://res\.cloudinary\.com/", re.I)
_UPLOAD_MARKER = "/image/upload/"
_TRANSFORM_SEGMENT = re.compile(r"^(f_|q_|w_|h_|c_|g_|dpr_|fl_)")


def configure_cloudinary() -> None:
    if not settings.cloudinary_configured:
        return
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


def is_cloudinary_url(url: str) -> bool:
    return bool(url and _CLOUDINARY_HOST.match(url.strip()))


def _delivery_path_tail(after_upload: str) -> str:
    """Strip existing delivery transforms; keep version + public_id path."""
    segments = after_upload.split("/")
    i = 0
    while i < len(segments):
        seg = segments[i]
        if re.fullmatch(r"v\d+", seg):
            return "/".join(segments[i:])
        if "," in seg or _TRANSFORM_SEGMENT.match(seg):
            i += 1
            continue
        return "/".join(segments[i:])
    return "/".join(segments)


def optimize_image_url(url: str, *, width: int) -> str:
    """Build a delivery URL with f_auto, q_auto:good and max width."""
    if not is_cloudinary_url(url) or _UPLOAD_MARKER not in url:
        return url

    base, after = url.split(_UPLOAD_MARKER, 1)
    transform = f"f_auto,q_auto:good,w_{width},c_limit"
    tail = _delivery_path_tail(after)
    return f"{base}{_UPLOAD_MARKER}{transform}/{tail}"


def upload_image(file_bytes: bytes, filename: str) -> dict:
    if not settings.cloudinary_configured:
        raise RuntimeError("Cloudinary is not configured. Set CLOUDINARY_* in .env")

    configure_cloudinary()
    base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
    base_name = re.sub(r"[^\w\-]+", "-", base_name).strip("-") or "service-image"

    return cloudinary.uploader.upload(
        file_bytes,
        folder=settings.cloudinary_folder,
        public_id=base_name,
        unique_filename=True,
        overwrite=False,
        resource_type="image",
        transformation=[
            {"width": UPLOAD_MAX_EDGE, "height": UPLOAD_MAX_EDGE, "crop": "limit"},
            {"quality": "auto:good", "fetch_format": "auto"},
        ],
    )
