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


class ServiceFormInput(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=1)
    image: str = ""
    image_alt: str = ""
    gallery: list[GalleryItem] = []


class ServiceFormUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    image: str | None = None
    image_alt: str | None = None
    gallery: list[GalleryItem] | None = None
    active: bool | None = None


class ServicePublic(BaseModel):
    slug: str
    title: str
    shortDescription: str
    chipLabel: str
    order: int
    active: bool
    image: str
    imageHero: str = ""
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
