import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.models import get_db, User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("DVMCP_JWT_SECRET", "dvmcp-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    total_points: int = 0
    challenges_completed: int = 0


class TokenResponse(BaseModel):
    token: str
    user: UserResponse

# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT containing *data* with an expiry claim."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Decode and verify a JWT.  Raises *HTTPException* on failure."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency that extracts and validates the current user from
    the Bearer token in the Authorization header."""
    payload = verify_token(credentials.credentials)
    user_id: int | None = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account and return a JWT."""
    if not body.username or not body.password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    if len(body.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")

    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")

    hashed = pwd_context.hash(body.password)
    user = User(username=body.username, password_hash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token({"user_id": user.id, "username": user.username})
    return TokenResponse(
        token=token,
        user=UserResponse(id=user.id, username=user.username),
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate an existing user and return a JWT."""
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token({"user_id": user.id, "username": user.username})
    return TokenResponse(
        token=token,
        user=UserResponse(id=user.id, username=user.username),
    )


# ---------------------------------------------------------------------------
# User profile & progress routes (placed here to share auth deps)
# ---------------------------------------------------------------------------

user_router = APIRouter(prefix="/api", tags=["user"])


@user_router.get("/user/profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user_obj: User = Depends(get_current_user),
):
    """Return the current user's profile with computed stats."""
    from database.models import Submission, HintUsage

    total_earned = sum(
        s.points_awarded
        for s in db.query(Submission).filter(
            Submission.user_id == current_user_obj.id, Submission.is_correct == True
        ).all()
    )
    total_spent = sum(
        h.points_cost
        for h in db.query(HintUsage).filter(HintUsage.user_id == current_user_obj.id).all()
    )
    completed = (
        db.query(Submission.challenge_id)
        .filter(Submission.user_id == current_user_obj.id, Submission.is_correct == True)
        .distinct()
        .count()
    )
    return {
        "id": current_user_obj.id,
        "username": current_user_obj.username,
        "total_points": total_earned - total_spent,
        "challenges_completed": completed,
    }


@user_router.get("/user/progress")
def get_progress(
    db: Session = Depends(get_db),
    current_user_obj: User = Depends(get_current_user),
):
    """Return challenge progress for the current user."""
    from database.models import Progress
    rows = db.query(Progress).filter(Progress.user_id == current_user_obj.id).all()
    return [
        {
            "challenge_id": p.challenge_id,
            "status": p.status,
            "started_at": p.started_at.isoformat() if p.started_at else None,
            "completed_at": p.completed_at.isoformat() if p.completed_at else None,
        }
        for p in rows
    ]
