import re

from app.schemas import GalleryItem

_UPLOAD_MARKER = "/image/upload/"
_TRANSFORM_SEGMENT = re.compile(r"^(f_|q_|w_|h_|c_|g_|dpr_|fl_)")


def normalize_image_url(url: str) -> str:
    """Canonical key for deduplicating the same Cloudinary asset with different transforms."""
    url = (url or "").strip().split("?")[0]
    if not url or _UPLOAD_MARKER not in url:
        return url

    base, after = url.split(_UPLOAD_MARKER, 1)
    segments = after.split("/")
    i = 0
    while i < len(segments):
        seg = segments[i]
        if re.fullmatch(r"v\d+", seg):
            return f"{base}{_UPLOAD_MARKER}{'/'.join(segments[i:])}".lower()
        if "," in seg or _TRANSFORM_SEGMENT.match(seg):
            i += 1
            continue
        return f"{base}{_UPLOAD_MARKER}{'/'.join(segments[i:])}".lower()
    return url.lower()


def merge_service_gallery_items(
    *,
    image: str,
    image_alt: str,
    gallery: list[dict | GalleryItem] | None,
) -> list[dict[str, str]]:
    """
    Build the public gallery: main image first, then extra gallery images.
    Skips duplicates (same Cloudinary asset under different delivery URLs).
    """
    merged: list[dict[str, str]] = []
    seen: set[str] = set()
    fallback_alt = (image_alt or "").strip()

    def add(src: str, alt: str) -> None:
        src = (src or "").strip()
        if not src:
            return
        key = normalize_image_url(src)
        if key in seen:
            return
        seen.add(key)
        merged.append({"src": src, "alt": (alt or fallback_alt).strip()})

    add(image, fallback_alt)

    for item in gallery or []:
        raw = item if isinstance(item, dict) else item.model_dump()
        add(raw.get("src", ""), raw.get("alt", "") or fallback_alt)

    return merged
