"""Organization repository: MongoDB CRUD with UUID _id."""

import uuid
from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.organization import OrganizationDocument

COLLECTION = "organizations"


def _serialize(doc: dict[str, Any]) -> dict[str, Any]:
    if not doc:
        return doc
    out = dict(doc)
    if "_id" in out:
        out["id"] = out.pop("_id")
    for key in ("created_at", "updated_at"):
        if key in out and isinstance(out[key], datetime):
            out[key] = out[key].isoformat()
    return out


class OrganizationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    async def create_indexes(self) -> None:
        # _id is already unique by default in MongoDB; no need to create it
        pass

    async def insert(self, org: OrganizationDocument) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = org.model_dump(mode="json")
        doc["_id"] = uuid.uuid4().hex
        doc["created_at"] = now
        doc["updated_at"] = now
        await self.collection.insert_one(doc)
        return _serialize(doc)

    async def get_by_id(self, org_id: str) -> dict[str, Any] | None:
        doc = await self.collection.find_one({"_id": org_id})
        return _serialize(doc) if doc else None

    async def list_all(self) -> list[dict[str, Any]]:
        cursor = self.collection.find({}).sort("created_at", -1)
        docs = await cursor.to_list(length=1000)
        return [_serialize(d) for d in docs]

    async def update(self, org_id: str, update: dict[str, Any]) -> dict[str, Any] | None:
        update["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.find_one_and_update(
            {"_id": org_id},
            {"$set": update},
            return_document=True,
        )
        return _serialize(result) if result else None
