from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from models import UserRole, DiagnosticType, SeverityLevel, VerificationStatus

# ── User schemas ──────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.USER

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

# ── Mechanic schemas ──────────────────────────────────────────────────────────

class MechanicBase(BaseModel):
    business_name: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class MechanicCreate(MechanicBase):
    pass

class MechanicUpdate(MechanicBase):
    pass

class Mechanic(MechanicBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    certificate_url: Optional[str] = None
    verification_status: VerificationStatus
    rating: float
    total_ratings: int
    created_at: datetime
    user: User

# ── Diagnostic schemas ────────────────────────────────────────────────────────

class DiagnosticBase(BaseModel):
    type: DiagnosticType
    title: str
    description: Optional[str] = None

class DiagnosticCreate(DiagnosticBase):
    pass

class VideoLink(BaseModel):
    title: str
    url: str

class DiagnosticResult(BaseModel):
    issue: str
    confidence: float
    description: str
    recommendation: str
    severity: SeverityLevel
    video_links: List[VideoLink] = []

class Diagnostic(DiagnosticBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    file_url: Optional[str] = None
    confidence_score: Optional[float] = None
    severity: Optional[SeverityLevel] = None
    result: Optional[DiagnosticResult] = None
    created_at: datetime

# ── Feedback schemas ──────────────────────────────────────────────────────────

class FeedbackBase(BaseModel):
    rating: int
    message: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    mechanic_id: Optional[int] = None
    diagnostic_id: Optional[int] = None

class Feedback(FeedbackBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    mechanic_id: Optional[int] = None
    diagnostic_id: Optional[int] = None
    created_at: datetime

# ── Token schemas ─────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    email: Optional[str] = None
