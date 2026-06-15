import cloudinary
import cloudinary.uploader

from app.config import settings


def configure_cloudinary() -> None:
    if not settings.cloudinary_configured:
        return
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


def upload_image(file_bytes: bytes, filename: str) -> dict:
    if not settings.cloudinary_configured:
        raise RuntimeError("Cloudinary is not configured. Set CLOUDINARY_* in .env")

    configure_cloudinary()
    return cloudinary.uploader.upload(
        file_bytes,
        folder=settings.cloudinary_folder,
        public_id=filename.rsplit(".", 1)[0] if "." in filename else filename,
        overwrite=True,
        resource_type="image",
    )
