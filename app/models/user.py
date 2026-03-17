"""User document and role enum."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    CAMPAIGN_MANAGER = "campaign_manager"
    ANALYST = "analyst"
    CLIENT = "client"


class OAuthProviderLink(BaseModel):
    """Linked OAuth provider (Google, Microsoft)."""

    provider: str  # "google" | "microsoft"
    provider_user_id: str


class UserDocument(BaseModel):
    """MongoDB user document."""

    first_name: str
    last_name: str
    email: str  # stored lowercase
    hashed_password: str | None = None  # None if OAuth-only
    role: UserRole = UserRole.CLIENT
    profile_picture: str | None = None
    language: str = "en"
    timezone: str | None = None

    email_verified: bool = False
    is_active: bool = True
    organization_id: str | None = None  # single org (spec); null for SUPER_ADMIN
    organization_ids: list[str] = Field(default_factory=list)  # legacy
    oauth_providers: list[OAuthProviderLink] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: datetime | None = None

    model_config = {"extra": "allow"}

    def to_mongo(self) -> dict[str, Any]:
        d = self.model_dump(mode="json")
        for item in d.get("oauth_providers", []):
            if hasattr(item, "model_dump"):
                pass  # already dict in mode=json
        return d
