"""Invitation repository: MongoDB CRUD with UUID _id."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.invitation import InvitationDocument

COLLECTION = "invitations"


def _serialize(doc: dict[str, Any]) -> dict[str, Any]:
    if not doc:
        return doc
    out = dict(doc)
    if "_id" in out:
        out["id"] = out.pop("_id")
    for key in ("created_at", "expires_at"):
        if key in out and isinstance(out[key], datetime):
            out[key] = out[key].isoformat()
    return out


class InvitationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    async def create_indexes(self) -> None:
        await self.collection.create_index("token", unique=True)
        await self.collection.create_index("organization_id")
        await self.collection.create_index("email")

    async def insert(self, inv: InvitationDocument) -> dict[str, Any]:
        doc = inv.model_dump(mode="json")
        doc["_id"] = uuid.uuid4().hex
        doc["email"] = doc["email"].lower().strip()
        await self.collection.insert_one(doc)
        return _serialize(doc)

    async def get_by_token(self, token: str) -> dict[str, Any] | None:
        doc = await self.collection.find_one({"token": token})
        return _serialize(doc) if doc else None

    async def get_by_id(self, inv_id: str) -> dict[str, Any] | None:
        doc = await self.collection.find_one({"_id": inv_id})
        return _serialize(doc) if doc else None

    async def list_by_organization(self, organization_id: str) -> list[dict[str, Any]]:
        cursor = self.collection.find({"organization_id": organization_id}).sort("created_at", -1)
        return [_serialize(d) for d in await cursor.to_list(length=500)]

    async def update_status(self, inv_id: str, status: str) -> dict[str, Any] | None:
        result = await self.collection.find_one_and_update(
            {"_id": inv_id},
            {"$set": {"status": status}},
            return_document=True,
        )
        return _serialize(result) if result else None

    async def set_accepted(self, token: str) -> dict[str, Any] | None:
        result = await self.collection.find_one_and_update(
            {"token": token, "status": "PENDING"},
            {"$set": {"status": "ACCEPTED"}},
            return_document=True,
        )
        return _serialize(result) if result else None
