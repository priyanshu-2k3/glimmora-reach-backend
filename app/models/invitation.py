"""Invitation document for org invite flow."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class InvitationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"


# Roles allowed in invitations (no SUPER_ADMIN, ADMIN is created via create-admin)
INVITE_ROLES = ("ADMIN", "CAMPAIGN_MANAGER", "ANALYTICS", "VIEWER")


class InvitationDocument(BaseModel):
    """MongoDB invitation document."""

    email: str  # lowercase
    role: str  # ADMIN, CAMPAIGN_MANAGER, ANALYTICS, VIEWER
    organization_id: str  # UUID
    invited_by: str  # user id
    token: str
    status: str = "PENDING"  # PENDING, ACCEPTED, EXPIRED
    expires_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"extra": "allow"}

    def to_mongo(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
