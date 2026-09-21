from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.rate_limit import limiter
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.security.deps import get_current_user
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit(settings.register_rate_limit)
def register(request: Request, req: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthService(db).register(req.email, req.password, req.first_name, req.last_name)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.login_rate_limit)
def login(request: Request, req: LoginRequest, db: Session = Depends(get_db)):
    token = AuthService(db).login(req.email, req.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)):
    return user
