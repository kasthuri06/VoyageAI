"""
Authentication routes: /auth/register, /auth/login, /auth/google
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, UserPreference
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse, GoogleLoginRequest
from core.security import hash_password, verify_password, create_access_token

router = APIRouter()


def _role_val(role):
    return role.value if hasattr(role, "value") else role


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user and return a JWT token."""
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        is_verified=True,
    )
    db.add(user)
    db.flush()

    prefs = UserPreference(id=str(uuid.uuid4()), user_id=user_id)
    db.add(prefs)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        username=user.username,
        role=_role_val(user.role),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        username=user.username,
        role=_role_val(user.role),
    )


@router.post("/google", response_model=TokenResponse)
async def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Google OAuth login."""
    from config import settings
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=501, detail="Google login not configured")

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={payload.id_token}"
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid Google token")
            google_data = resp.json()

        if google_data.get("aud") != settings.GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=401, detail="Token audience mismatch")

        google_id = google_data["sub"]
        email     = google_data.get("email", "")
        full_name = google_data.get("name", "")
        picture   = google_data.get("picture", "")

        user = db.query(User).filter(User.google_id == google_id).first()
        if not user:
            user = db.query(User).filter(User.email == email).first()
            if user:
                user.google_id = google_id
            else:
                user_id  = str(uuid.uuid4())
                username = email.split("@")[0] + "_" + str(uuid.uuid4())[:4]
                user = User(
                    id=user_id,
                    email=email,
                    username=username,
                    google_id=google_id,
                    full_name=full_name,
                    profile_picture=picture,
                    is_verified=True,
                )
                db.add(user)
                db.flush()
                db.add(UserPreference(id=str(uuid.uuid4()), user_id=user_id))

        db.commit()
        db.refresh(user)

        token = create_access_token({"sub": str(user.id)})
        return TokenResponse(
            access_token=token,
            user_id=str(user.id),
            username=user.username,
            role=_role_val(user.role),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google login failed: {str(e)}")
