"""Organization request/response schemas."""

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class OrganizationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    is_active: bool | None = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    created_by: str | None = None
    is_active: bool = True
    created_at: str
    updated_at: str | None = None
    member_count: int | None = None
