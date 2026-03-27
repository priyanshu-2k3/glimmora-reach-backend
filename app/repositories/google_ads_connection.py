"""Repository for storing per-user Google Ads OAuth connections."""

from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase


class GoogleAdsConnectionRepository:
    COLLECTION = "ads_connections"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def save_connection(
        self,
        user_id: str,
        org_id: str | None,
        refresh_token: str,
        token_payload: dict | None = None,
    ) -> str:
        """Upsert a connection for the user (one connection per user)."""
        now = datetime.now(timezone.utc)
        token_payload = token_payload or {}
        await self.db[self.COLLECTION].update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "org_id": org_id,
                    "refresh_token": refresh_token,
                    "access_token": token_payload.get("access_token"),
                    "scope": token_payload.get("scope"),
                    "token_type": token_payload.get("token_type"),
                    "expires_in": token_payload.get("expires_in"),
                    "token_received_at": now,
                    "connected_at": now,
                    "updated_at": now,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )
        return user_id

    async def get_connection(self, user_id: str) -> dict | None:
        """Return the connection doc for a user, without _id."""
        return await self.db[self.COLLECTION].find_one(
            {"user_id": user_id}, {"_id": 0}
        )

    async def delete_connection(self, user_id: str) -> bool:
        result = await self.db[self.COLLECTION].delete_one({"user_id": user_id})
        return result.deleted_count > 0

    async def create_indexes(self):
        await self.db[self.COLLECTION].create_index("user_id", unique=True)
