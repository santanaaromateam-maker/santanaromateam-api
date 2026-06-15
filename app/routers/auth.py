from fastapi import APIRouter, Depends, HTTPException, status

from app.auth_utils import create_access_token, verify_password
from app.database import admins_collection
from app.deps import get_current_admin
from app.schemas import AdminProfile, LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    admin = admins_collection().find_one({"email": body.email.lower()})
    if not admin or not verify_password(body.password, admin["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return TokenResponse(access_token=create_access_token(admin["email"]))


@router.get("/me", response_model=AdminProfile)
def me(admin: dict = Depends(get_current_admin)):
    return AdminProfile(email=admin["email"])
