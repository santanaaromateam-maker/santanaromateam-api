from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.cloudinary_service import upload_image
from app.config import settings
from app.database import services_collection
from app.deps import get_current_admin
from app.schemas import GalleryItem, ServiceAdmin, ServiceFormInput, ServiceFormUpdate, UploadResponse
from app.service_fields import expand_service_fields
from app.services_mapper import service_to_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _parse_id(service_id: str) -> ObjectId:
    try:
        return ObjectId(service_id)
    except InvalidId as exc:
        raise HTTPException(status_code=404, detail="Service not found") from exc


def _next_order() -> int:
    last = services_collection().find_one(sort=[("order", -1)])
    return (last.get("order", -1) + 1) if last else 0


def _service_from_create(body: ServiceFormInput) -> dict:
    now = datetime.now(timezone.utc)
    fields = expand_service_fields(
        title=body.title,
        description=body.description,
        image=body.image,
        image_alt=body.image_alt,
        gallery=body.gallery,
        order=_next_order(),
        active=True,
    )
    return {**fields, "created_at": now, "updated_at": now}


@router.get("/services", response_model=list[ServiceAdmin])
def list_services(_: dict = Depends(get_current_admin)):
    cursor = services_collection().find().sort([("order", 1), ("_id", 1)])
    return [service_to_admin(doc) for doc in cursor]


@router.post("/services", response_model=ServiceAdmin, status_code=status.HTTP_201_CREATED)
def create_service(body: ServiceFormInput, _: dict = Depends(get_current_admin)):
    doc = _service_from_create(body)
    if services_collection().find_one({"slug": doc["slug"]}):
        raise HTTPException(status_code=400, detail="A service with this title already exists")

    result = services_collection().insert_one(doc)
    saved = services_collection().find_one({"_id": result.inserted_id})
    return service_to_admin(saved)


@router.put("/services/{service_id}", response_model=ServiceAdmin)
def update_service(service_id: str, body: ServiceFormUpdate, _: dict = Depends(get_current_admin)):
    oid = _parse_id(service_id)
    existing = services_collection().find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Service not found")

    updates = body.model_dump(exclude_unset=True)
    if not updates:
        return service_to_admin(existing)

    title = updates.get("title", existing["title"])
    intro = existing.get("intro") or []
    description = updates.get(
        "description",
        "\n\n".join(intro) if intro else existing.get("short_description", ""),
    )
    image = updates.get("image", existing.get("image", ""))
    image_alt = updates.get("image_alt", existing.get("image_alt", ""))
    gallery_raw = updates.get("gallery", existing.get("gallery") or [])
    gallery = [
        GalleryItem(**item) if isinstance(item, dict) else item for item in gallery_raw
    ]

    fields = expand_service_fields(
        title=title,
        description=description,
        image=image,
        image_alt=image_alt,
        gallery=gallery,
        order=existing.get("order", 0),
        active=updates.get("active", existing.get("active", True)),
    )

    if fields["slug"] != existing["slug"]:
        if services_collection().find_one({"slug": fields["slug"], "_id": {"$ne": oid}}):
            raise HTTPException(status_code=400, detail="A service with this title already exists")

    fields["updated_at"] = datetime.now(timezone.utc)
    services_collection().update_one({"_id": oid}, {"$set": fields})
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

    return UploadResponse(
        url=result["secure_url"],
        public_id=result["public_id"],
    )
