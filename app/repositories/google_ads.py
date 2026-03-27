"""MongoDB repository for Google Ads records."""

from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase


class GoogleAdsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def save(self, collection: str, data: dict) -> str:
        """Insert a document and return its string ID."""
        data["created_at"] = datetime.now(timezone.utc)
        result = await self.db[collection].insert_one(data)
        return str(result.inserted_id)

    async def list_all(self, collection: str) -> list[dict]:
        """Return all documents from a collection without _id."""
        cursor = self.db[collection].find({}, {"_id": 0})
        return await cursor.to_list(length=500)

    # ── Accounts ──────────────────────────────────────────────────────────────

    async def save_accessible_accounts(
        self,
        user_id: str,
        customer_resource_names: list[str],
    ) -> str:
        return await self.save("ads_accounts", {
            "user_id": user_id,
            "accounts": customer_resource_names,
            "count": len(customer_resource_names),
        })

    # ── Budgets ──────────────────────────────────────────────────────────────

    async def save_budget(self, customer_id: str, name: str, amount_inr: int,
                          delivery_method: str, resource_name: str) -> str:
        return await self.save("ads_budgets", {
            "customer_id": customer_id,
            "name": name,
            "amount_inr": amount_inr,
            "amount_micros": amount_inr * 1_000_000,
            "delivery_method": delivery_method,
            "resource_name": resource_name,
        })

    async def get_budgets(self) -> list[dict]:
        return await self.list_all("ads_budgets")

    # ── Campaigns ────────────────────────────────────────────────────────────

    async def save_campaign(self, customer_id: str, name: str, budget_resource: str,
                            channel_type: str, status: str, resource_name: str) -> str:
        return await self.save("ads_campaigns", {
            "customer_id": customer_id,
            "name": name,
            "budget_resource": budget_resource,
            "channel_type": channel_type,
            "status": status,
            "resource_name": resource_name,
        })

    async def save_deleted_campaign(self, customer_id: str, campaign_id: str) -> str:
        return await self.save("ads_deleted_campaigns", {
            "customer_id": customer_id,
            "campaign_id": campaign_id,
            "resource_name": f"customers/{customer_id}/campaigns/{campaign_id}",
        })

    async def get_campaigns(self) -> list[dict]:
        return await self.list_all("ads_campaigns")

    # ── Ad Groups ─────────────────────────────────────────────────────────────

    async def save_adgroup(self, customer_id: str, name: str, campaign_resource: str,
                           type_: str, status: str, cpc_bid_inr: int,
                           resource_name: str) -> str:
        return await self.save("ads_adgroups", {
            "customer_id": customer_id,
            "name": name,
            "campaign_resource": campaign_resource,
            "type": type_,
            "status": status,
            "cpc_bid_inr": cpc_bid_inr,
            "cpc_bid_micros": cpc_bid_inr * 1_000_000,
            "resource_name": resource_name,
        })

    async def get_adgroups(self) -> list[dict]:
        return await self.list_all("ads_adgroups")

    # ── Ads ───────────────────────────────────────────────────────────────────

    async def save_ad(self, customer_id: str, ad_group_resource: str, final_url: str,
                      headlines: list[str], descriptions: list[str],
                      status: str, resource_name: str) -> str:
        return await self.save("ads_ads", {
            "customer_id": customer_id,
            "ad_group_resource": ad_group_resource,
            "final_url": final_url,
            "headlines": headlines,
            "descriptions": descriptions,
            "status": status,
            "resource_name": resource_name,
        })

    async def get_ads(self) -> list[dict]:
        return await self.list_all("ads_ads")

    # ── Keywords ──────────────────────────────────────────────────────────────

    async def save_keywords(self, customer_id: str, ad_group_resource: str,
                            keywords: list[str], match_type: str,
                            resource_names: list[str]) -> str:
        return await self.save("ads_keywords", {
            "customer_id": customer_id,
            "ad_group_resource": ad_group_resource,
            "keywords": keywords,
            "match_type": match_type,
            "resource_names": resource_names,
        })

    async def get_keywords(self) -> list[dict]:
        return await self.list_all("ads_keywords")

    # ── Metrics ───────────────────────────────────────────────────────────────

    async def save_metrics(self, customer_id: str, metrics: list[dict]) -> str:
        return await self.save("ads_metrics", {
            "customer_id": customer_id,
            "metrics": metrics,
        })

    async def get_latest_metrics(self, customer_id: str) -> list[dict]:
        doc = await self.db["ads_metrics"].find_one(
            {"customer_id": customer_id},
            {"_id": 0},
            sort=[("created_at", -1)],
        )
        if doc:
            return doc.get("metrics", [])
        return []

    # ── Insights ─────────────────────────────────────────────────────────────

    async def save_insights(self, customer_id: str, insights: list[dict]) -> str:
        return await self.save("ads_insights", {
            "customer_id": customer_id,
            "insights": insights,
        })

    async def get_latest_insights(self, customer_id: str) -> dict | None:
        return await self.db["ads_insights"].find_one(
            {"customer_id": customer_id},
            {"_id": 0},
            sort=[("created_at", -1)],
        )
