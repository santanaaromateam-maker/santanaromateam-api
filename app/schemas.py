from pydantic import BaseModel, EmailStr, Field


class GalleryItem(BaseModel):
    src: str
    alt: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminProfile(BaseModel):
    email: EmailStr


class ServiceBase(BaseModel):
    slug: str = Field(min_length=2, max_length=120)
    title: str = Field(min_length=2, max_length=200)
    short_description: str
    chip_label: str
    order: int = 0
    active: bool = True
    image: str = ""
    image_alt: str = ""
    hero_title: str = ""
    hero_subtitle: str = ""
    meta_description: str = ""
    intro: list[str] = []
    gallery: list[GalleryItem] = []
    service_areas: list[str] = []
    whatsapp_text: str = ""


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    slug: str | None = None
    title: str | None = None
    short_description: str | None = None
    chip_label: str | None = None
    order: int | None = None
    active: bool | None = None
    image: str | None = None
    image_alt: str | None = None
    hero_title: str | None = None
    hero_subtitle: str | None = None
    meta_description: str | None = None
    intro: list[str] | None = None
    gallery: list[GalleryItem] | None = None
    service_areas: list[str] | None = None
    whatsapp_text: str | None = None


class ServicePublic(BaseModel):
    slug: str
    title: str
    shortDescription: str
    chipLabel: str
    order: int
    active: bool
    image: str
    imageAlt: str
    heroTitle: str
    heroSubtitle: str
    metaDescription: str
    intro: list[str]
    gallery: list[GalleryItem]
    serviceAreas: list[str]
    whatsappText: str

    model_config = {"from_attributes": True}


class ServiceAdmin(ServicePublic):
    id: str


class ServicesPublicResponse(BaseModel):
    services: list[ServicePublic]


class UploadResponse(BaseModel):
    url: str
    public_id: str
