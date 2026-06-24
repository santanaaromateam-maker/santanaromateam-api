import re

from app.auth_utils import slugify
from app.schemas import GalleryItem

DEFAULT_SERVICE_AREAS = [
    "Hollywood, FL",
    "Plantation, FL",
    "Fort Lauderdale, FL",
    "Aventura, FL",
    "Pembroke Pines, FL",
    "Miramar, FL",
    "Davie, FL",
    "Sunrise, FL",
]


def _plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _first_paragraph(description: str) -> str:
    parts = [p.strip() for p in re.split(r"\n\s*\n", description.strip()) if p.strip()]
    return parts[0] if parts else description.strip()


def _intro_paragraphs(description: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"\n\s*\n", description.strip()) if p.strip()]
    return parts if parts else ([description.strip()] if description.strip() else [])


def _meta_description(description: str, max_len: int = 155) -> str:
    text = _plain_text(description)
    if len(text) <= max_len:
        return text
    trimmed = text[: max_len - 3].rsplit(" ", 1)[0]
    return f"{trimmed}..."


def _short_description(description: str, max_len: int = 220) -> str:
    first = _first_paragraph(description)
    text = _plain_text(first)
    if len(text) <= max_len:
        return text
    trimmed = text[: max_len - 3].rsplit(" ", 1)[0]
    return f"{trimmed}..."


def _gallery_with_alt(gallery: list[GalleryItem], title: str, image_alt: str) -> list[dict]:
    fallback_alt = image_alt.strip() or title.strip()
    result = []
    for index, item in enumerate(gallery):
        alt = item.alt.strip() if item.alt else fallback_alt
        if len(gallery) > 1 and alt == fallback_alt:
            alt = f"{fallback_alt} ({index + 1})"
        result.append({"src": item.src, "alt": alt})
    return result


def expand_service_fields(
    *,
    title: str,
    description: str,
    image: str = "",
    image_alt: str = "",
    gallery: list[GalleryItem] | None = None,
    order: int = 0,
    active: bool = True,
    is_commercial: bool = True,
) -> dict:
    title = title.strip()
    description = description.strip()
    image_alt = image_alt.strip() or title

    return {
        "slug": slugify(title),
        "title": title,
        "short_description": _short_description(description),
        "chip_label": title,
        "order": order,
        "active": active,
        "image": image.strip(),
        "image_alt": image_alt,
        "hero_title": title,
        "hero_subtitle": _first_paragraph(description),
        "meta_description": _meta_description(description),
        "intro": _intro_paragraphs(description),
        "gallery": _gallery_with_alt(gallery or [], title, image_alt),
        "service_areas": DEFAULT_SERVICE_AREAS.copy(),
        "whatsapp_text": f"Hi, I need {title}.",
        "is_commercial": is_commercial,
    }
