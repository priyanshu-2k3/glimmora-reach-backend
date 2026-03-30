"""MongoDB repository for Meta (Facebook) Ads records."""

from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase


class MetaAdsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def save(self, collection: str, data: dict) -> str:
        """Insert a document and return its string ID."""
        data["created_at"] = datetime.now(timezone.utc)
        result = await self.db[collection].insert_one(data)
        return str(result.inserted_id)

    async def list_all(self, collection: str, filter_: dict | None = None) -> list[dict]:
        """Return all documents from a collection without _id."""
        cursor = self.db[collection].find(filter_ or {}, {"_id": 0})
        return await cursor.to_list(length=500)

    # -- Campaigns ---------------------------------------------------------------

    async def save_campaign(self, user_id: str, ad_account_id: str, data: dict) -> str:
        return await self.save("meta_campaigns", {
            "user_id": user_id,
            "ad_account_id": ad_account_id,
            **data,
        })

    async def get_campaigns(self, user_id: str) -> list[dict]:
        return await self.list_all("meta_campaigns", {"user_id": user_id})

    # -- Ad Sets -----------------------------------------------------------------

    async def save_adset(self, user_id: str, ad_account_id: str, data: dict) -> str:
        return await self.save("meta_adsets", {
            "user_id": user_id,
            "ad_account_id": ad_account_id,
            **data,
        })

    async def get_adsets(self, user_id: str) -> list[dict]:
        return await self.list_all("meta_adsets", {"user_id": user_id})

    # -- Creatives ---------------------------------------------------------------

    async def save_creative(self, user_id: str, ad_account_id: str, data: dict) -> str:
        return await self.save("meta_creatives", {
            "user_id": user_id,
            "ad_account_id": ad_account_id,
            **data,
        })

    async def get_creatives(self, user_id: str) -> list[dict]:
        return await self.list_all("meta_creatives", {"user_id": user_id})

    # -- Ads ---------------------------------------------------------------------

    async def save_ad(self, user_id: str, ad_account_id: str, data: dict) -> str:
        return await self.save("meta_ads", {
            "user_id": user_id,
            "ad_account_id": ad_account_id,
            **data,
        })

    async def get_ads(self, user_id: str) -> list[dict]:
        return await self.list_all("meta_ads", {"user_id": user_id})

    # -- Media -------------------------------------------------------------------

    async def save_media(self, user_id: str, ad_account_id: str, data: dict) -> str:
        return await self.save("meta_media", {
            "user_id": user_id,
            "ad_account_id": ad_account_id,
            **data,
        })

    async def get_media(self, user_id: str) -> list[dict]:
        return await self.list_all("meta_media", {"user_id": user_id})

    # -- Custom Audiences --------------------------------------------------------

    async def save_audience(self, user_id: str, ad_account_id: str, data: dict) -> str:
        return await self.save("meta_audiences", {
            "user_id": user_id,
            "ad_account_id": ad_account_id,
            **data,
        })

    async def get_audiences(self, user_id: str) -> list[dict]:
        return await self.list_all("meta_audiences", {"user_id": user_id})

    # -- Lead Forms --------------------------------------------------------------

    async def save_lead_form(self, user_id: str, page_id: str, data: dict) -> str:
        return await self.save("meta_lead_forms", {
            "user_id": user_id,
            "page_id": page_id,
            **data,
        })

    async def get_lead_forms(self, user_id: str) -> list[dict]:
        return await self.list_all("meta_lead_forms", {"user_id": user_id})

    # -- Lead Responses ----------------------------------------------------------

    async def save_leads(self, user_id: str, form_id: str, leads: list[dict]) -> str:
        return await self.save("meta_leads", {
            "user_id": user_id,
            "form_id": form_id,
            "leads": leads,
            "count": len(leads),
        })

    async def get_leads(self, user_id: str) -> list[dict]:
        return await self.list_all("meta_leads", {"user_id": user_id})

    # -- Insights ----------------------------------------------------------------

    async def save_insights(self, user_id: str, object_id: str, data: dict) -> str:
        return await self.save("meta_insights", {
            "user_id": user_id,
            "object_id": object_id,
            **data,
        })

    async def get_latest_insights(self, user_id: str, object_id: str) -> dict | None:
        return await self.db["meta_insights"].find_one(
            {"user_id": user_id, "object_id": object_id},
            {"_id": 0},
            sort=[("created_at", -1)],
        )
