"""Organization document per backend-api-spec."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class OrganizationDocument(BaseModel):
    """MongoDB organization document. _id is UUID set in repo on insert."""

    name: str
    created_by: str  # user id (SUPER_ADMIN)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"extra": "allow"}

    def to_mongo(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
