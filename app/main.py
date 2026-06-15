from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.cloudinary_service import configure_cloudinary
from app.config import settings
from app.database import close_db
from app.routers import admin, auth, public
from app.seed import init_db

WEB_ROOT = Path(__file__).resolve().parents[2] / "web"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    configure_cloudinary()
    yield
    close_db()


app = FastAPI(title="Santana Aroma API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "database": "mongodb",
        "mongodb_db": settings.mongodb_db_name,
        "cloudinary": settings.cloudinary_configured,
        "cors_origins": settings.cors_origin_list,
    }


@app.get("/services/{slug}")
@app.get("/services/{slug}/")
def service_detail_page(slug: str):
    """SPA template for dynamic service pages (local dev; Netlify uses _redirects)."""
    return FileResponse(WEB_ROOT / "services" / "index.html")


if WEB_ROOT.is_dir():
    app.mount("/", StaticFiles(directory=str(WEB_ROOT), html=True), name="web")
