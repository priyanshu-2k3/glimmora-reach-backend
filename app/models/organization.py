"""Organization document for multi-tenant support."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class OrganizationDocument(BaseModel):
    """MongoDB organization document."""

    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"extra": "allow"}

    def to_mongo(self) -> dict[str, Any]:
        d = self.model_dump()
        for k in ("created_at", "updated_at"):
            if k in d and isinstance(d[k], datetime):
                d[k] = d[k]
        return d
