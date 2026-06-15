from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.cloudinary_service import upload_image
from app.config import settings
from app.database import services_collection
from app.deps import get_current_admin
from app.schemas import ServiceAdmin, ServiceCreate, ServiceUpdate, UploadResponse
from app.services_mapper import service_to_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _parse_id(service_id: str) -> ObjectId:
    try:
        return ObjectId(service_id)
    except InvalidId as exc:
        raise HTTPException(status_code=404, detail="Service not found") from exc


def _service_from_create(body: ServiceCreate) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "slug": body.slug,
        "title": body.title,
        "short_description": body.short_description,
        "chip_label": body.chip_label,
        "order": body.order,
        "active": body.active,
        "image": body.image,
        "image_alt": body.image_alt,
        "hero_title": body.hero_title,
        "hero_subtitle": body.hero_subtitle,
        "meta_description": body.meta_description,
        "intro": body.intro,
        "gallery": [g.model_dump() for g in body.gallery],
        "service_areas": body.service_areas,
        "whatsapp_text": body.whatsapp_text,
        "created_at": now,
        "updated_at": now,
    }


@router.get("/services", response_model=list[ServiceAdmin])
def list_services(_: dict = Depends(get_current_admin)):
    cursor = services_collection().find().sort([("order", 1), ("_id", 1)])
    return [service_to_admin(doc) for doc in cursor]


@router.post("/services", response_model=ServiceAdmin, status_code=status.HTTP_201_CREATED)
def create_service(body: ServiceCreate, _: dict = Depends(get_current_admin)):
    if services_collection().find_one({"slug": body.slug}):
        raise HTTPException(status_code=400, detail="Slug already exists")

    result = services_collection().insert_one(_service_from_create(body))
    doc = services_collection().find_one({"_id": result.inserted_id})
    return service_to_admin(doc)


@router.put("/services/{service_id}", response_model=ServiceAdmin)
def update_service(service_id: str, body: ServiceUpdate, _: dict = Depends(get_current_admin)):
    oid = _parse_id(service_id)
    existing = services_collection().find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Service not found")

    data = body.model_dump(exclude_unset=True)
    if "slug" in data and data["slug"] != existing["slug"]:
        if services_collection().find_one({"slug": data["slug"]}):
            raise HTTPException(status_code=400, detail="Slug already exists")

    if "gallery" in data and data["gallery"] is not None:
        data["gallery"] = [g.model_dump() if hasattr(g, "model_dump") else g for g in data["gallery"]]

    if not data:
        return service_to_admin(existing)

    data["updated_at"] = datetime.now(timezone.utc)
    services_collection().update_one({"_id": oid}, {"$set": data})
    doc = services_collection().find_one({"_id": oid})
    return service_to_admin(doc)


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: str, _: dict = Depends(get_current_admin)):
    oid = _parse_id(service_id)
    result = services_collection().delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")


@router.post("/upload", response_model=UploadResponse)
async def upload_service_image(
    file: UploadFile = File(...),
    _: dict = Depends(get_current_admin),
):
    if not settings.cloudinary_configured:
        raise HTTPException(
            status_code=503,
            detail="Cloudinary is not configured. Add CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET to .env",
        )

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be under 10 MB")

    try:
        result = upload_image(contents, file.filename or "service-image")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Cloudinary upload failed: {exc}") from exc

    return UploadResponse(url=result["secure_url"], public_id=result["public_id"])
