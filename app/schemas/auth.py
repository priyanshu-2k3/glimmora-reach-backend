"""Auth and user request/response schemas."""

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Registration body."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.CLIENT
    language: str = Field(default="en", max_length=10)


class UserProfile(BaseModel):
    """Public user profile (response)."""

    id: str
    first_name: str
    last_name: str
    email: str
    role: UserRole
    profile_picture: str | None = None
    language: str
    timezone: str | None = None
    email_verified: bool
    is_active: bool
    organization_ids: list[str] = Field(default_factory=list)
    created_at: str  # ISO datetime
    last_login_at: str | None = None


class UserProfileUpdate(BaseModel):
    """PATCH profile body (all optional)."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    profile_picture: str | None = None
    language: str | None = Field(None, max_length=10)
    timezone: str | None = None


class ChangePasswordBody(BaseModel):
    """Change password body."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class TokenPayload(BaseModel):
    """JWT payload (sub = user id, type = access | refresh)."""

    sub: str
    type: str  # "access" | "refresh"
    email: str | None = None


class UserLoginShape(BaseModel):
    """User object in login/me response (spec: id, name, role lowercase, orgId, etc.)."""
    id: str
    name: str
    email: str
    role: str  # super_admin, admin, campaign_manager, analyst, client
    orgId: str | None = None
    avatar: str | None = None
    createdAt: str


class LoginResponse(BaseModel):
    """Login/refresh response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserLoginShape | None = None  # spec: include for login/accept-invite


class AcceptInviteBody(BaseModel):
    token: str = Field(..., min_length=1)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
