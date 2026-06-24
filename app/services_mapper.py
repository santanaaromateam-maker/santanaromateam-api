from app.cloudinary_service import WIDTH_CARD, WIDTH_GALLERY, WIDTH_HERO, optimize_image_url
from app.gallery_utils import merge_service_gallery_items
from app.schemas import GalleryItem, ServiceAdmin, ServicePublic


def _gallery_for_public(doc: dict) -> list[GalleryItem]:
    merged = merge_service_gallery_items(
        image=doc.get("image", ""),
        image_alt=doc.get("image_alt", ""),
        gallery=doc.get("gallery") or [],
    )
    return [
        GalleryItem(
            src=optimize_image_url(item["src"], width=WIDTH_GALLERY),
            alt=item["alt"],
        )
        for item in merged
    ]


def service_to_public(doc: dict) -> ServicePublic:
    image = doc.get("image", "")
    return ServicePublic(
        slug=doc["slug"],
        title=doc["title"],
        shortDescription=doc["short_description"],
        chipLabel=doc["chip_label"],
        order=doc.get("order", 0),
        active=doc.get("active", True),
        image=optimize_image_url(image, width=WIDTH_CARD),
        imageHero=optimize_image_url(image, width=WIDTH_HERO),
        imageAlt=doc.get("image_alt", ""),
        heroTitle=doc.get("hero_title", ""),
        heroSubtitle=doc.get("hero_subtitle", ""),
        metaDescription=doc.get("meta_description", ""),
        intro=doc.get("intro") or [],
        gallery=_gallery_for_public(doc),
        serviceAreas=doc.get("service_areas") or [],
        whatsappText=doc.get("whatsapp_text", ""),
        isCommercial=doc.get("is_commercial", True),
    )


def _gallery_raw(doc: dict) -> list[GalleryItem]:
    return [
        GalleryItem(**item) if isinstance(item, dict) else item for item in (doc.get("gallery") or [])
    ]


def service_to_admin(doc: dict) -> ServiceAdmin:
    return ServiceAdmin(
        id=str(doc["_id"]),
        slug=doc["slug"],
        title=doc["title"],
        shortDescription=doc["short_description"],
        chipLabel=doc["chip_label"],
        order=doc.get("order", 0),
        active=doc.get("active", True),
        image=doc.get("image", ""),
        imageHero=doc.get("image", ""),
        imageAlt=doc.get("image_alt", ""),
        heroTitle=doc.get("hero_title", ""),
        heroSubtitle=doc.get("hero_subtitle", ""),
        metaDescription=doc.get("meta_description", ""),
        intro=doc.get("intro") or [],
        gallery=_gallery_raw(doc),
        serviceAreas=doc.get("service_areas") or [],
        whatsappText=doc.get("whatsapp_text", ""),
        isCommercial=doc.get("is_commercial", True),
    )
