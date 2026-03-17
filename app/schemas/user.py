"""User management request/response schemas (create-admin, invite, list)."""

from pydantic import BaseModel, EmailStr, Field

from app.models.constants import ROLE_ADMIN, ROLE_ANALYTICS, ROLE_CAMPAIGN_MANAGER, ROLE_VIEWER


class CreateAdminBody(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    organization_id: str = Field(..., min_length=1)


class InviteBody(BaseModel):
    email: EmailStr
    role: str = Field(..., pattern=f"^({ROLE_CAMPAIGN_MANAGER}|{ROLE_ANALYTICS}|{ROLE_VIEWER})$")


class InvitationResponse(BaseModel):
    id: str
    email: str
    role: str
    status: str = "PENDING"
    expires_at: str


class UserRoleUpdateBody(BaseModel):
    role: str = Field(..., min_length=1)


class UserListItem(BaseModel):
    id: str
    name: str
    email: str
    role: str  # response role (lowercase)
    is_active: bool
    created_at: str
