from app.schemas import GalleryItem, ServiceAdmin, ServicePublic


def service_to_public(doc: dict) -> ServicePublic:
    gallery = [
        GalleryItem(**item) if isinstance(item, dict) else item for item in (doc.get("gallery") or [])
    ]
    return ServicePublic(
        slug=doc["slug"],
        title=doc["title"],
        shortDescription=doc["short_description"],
        chipLabel=doc["chip_label"],
        order=doc.get("order", 0),
        active=doc.get("active", True),
        image=doc.get("image", ""),
        imageAlt=doc.get("image_alt", ""),
        heroTitle=doc.get("hero_title", ""),
        heroSubtitle=doc.get("hero_subtitle", ""),
        metaDescription=doc.get("meta_description", ""),
        intro=doc.get("intro") or [],
        gallery=gallery,
        serviceAreas=doc.get("service_areas") or [],
        whatsappText=doc.get("whatsapp_text", ""),
    )


def service_to_admin(doc: dict) -> ServiceAdmin:
    public = service_to_public(doc)
    return ServiceAdmin(id=str(doc["_id"]), **public.model_dump())
