"""User repository: MongoDB CRUD."""

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.user import UserDocument, UserRole

COLLECTION = "users"


def _serialize_user(doc: dict[str, Any]) -> dict[str, Any]:
    """Add id (str) and normalize dates for response."""
    if not doc:
        return doc
    out = dict(doc)
    if "_id" in out:
        out["id"] = str(out.pop("_id"))
    for key in ("created_at", "updated_at", "last_login_at"):
        if key in out and isinstance(out[key], datetime):
            out[key] = out[key].isoformat()
    return out


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION]

    async def create_indexes(self) -> None:
        await self.collection.create_index("email", unique=True)
        await self.collection.create_index("oauth_providers.provider")
        await self.collection.create_index("oauth_providers.provider_user_id")

    async def get_by_id(self, user_id: str) -> dict[str, Any] | None:
        if not ObjectId.is_valid(user_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        return _serialize_user(doc) if doc else None

    async def get_by_email(self, email: str) -> dict[str, Any] | None:
        doc = await self.collection.find_one({"email": email.lower().strip()})
        return _serialize_user(doc) if doc else None

    async def get_by_oauth(self, provider: str, provider_user_id: str) -> dict[str, Any] | None:
        doc = await self.collection.find_one(
            {
                "oauth_providers": {
                    "$elemMatch": {"provider": provider, "provider_user_id": provider_user_id}
                }
            }
        )
        return _serialize_user(doc) if doc else None

    async def insert(self, user: UserDocument) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = user.model_dump(mode="json")
        doc["email"] = doc["email"].lower().strip()
        doc["created_at"] = now
        doc["updated_at"] = now
        # Convert oauth_providers items to dict
        if "oauth_providers" in doc:
            doc["oauth_providers"] = [
                x if isinstance(x, dict) else x.model_dump()
                for x in doc["oauth_providers"]
            ]
        if "role" in doc and hasattr(doc["role"], "value"):
            doc["role"] = doc["role"].value
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _serialize_user(doc)

    async def update(
        self,
        user_id: str,
        update: dict[str, Any],
    ) -> dict[str, Any] | None:
        if not ObjectId.is_valid(user_id):
            return None
        update["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update},
            return_document=True,
        )
        return _serialize_user(result) if result else None

    async def set_last_login(self, user_id: str) -> None:
        if not ObjectId.is_valid(user_id):
            return
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login_at": datetime.now(timezone.utc)}},
        )

    async def delete(self, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    async def add_oauth_provider(
        self,
        user_id: str,
        provider: str,
        provider_user_id: str,
    ) -> dict[str, Any] | None:
        if not ObjectId.is_valid(user_id):
            return None
        now = datetime.now(timezone.utc)
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {
                "$set": {"updated_at": now},
                "$addToSet": {
                    "oauth_providers": {
                        "provider": provider,
                        "provider_user_id": provider_user_id,
                    }
                },
            },
            return_document=True,
        )
        return _serialize_user(result) if result else None
