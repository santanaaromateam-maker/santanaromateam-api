from fastapi import APIRouter

from app.database import services_collection
from app.schemas import ServicesPublicResponse
from app.services_mapper import service_to_public

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/services", response_model=ServicesPublicResponse)
def list_public_services():
    cursor = services_collection().find({"active": True}).sort([("order", 1), ("_id", 1)])
    return ServicesPublicResponse(services=[service_to_public(doc) for doc in cursor])
