"""Google Ads API service — wraps the google-ads SDK."""

import uuid
from datetime import date, timedelta

from app.config import settings
from app.repositories.google_ads import GoogleAdsRepository
from app.services.google_ads_config import load_google_ads_base_config


def _get_client(refresh_token: str | None = None):
    """
    Load Google Ads client.
    If refresh_token is provided (user's own token from DB), use it.
    Otherwise fall back to google-ads.yaml.
    """
    from google.ads.googleads.client import GoogleAdsClient

    base = load_google_ads_base_config()
    if refresh_token:
        config = {
            "developer_token": base["developer_token"],
            "client_id": base["client_id"],
            "client_secret": base["client_secret"],
            "refresh_token": refresh_token,
            "use_proto_plus": base.get("use_proto_plus", True),
        }
        if base.get("login_customer_id"):
            config["login_customer_id"] = str(base["login_customer_id"])
        return GoogleAdsClient.load_from_dict(config)

    return GoogleAdsClient.load_from_dict(base)


def _get_service(client, service_name: str):
    """Always use configured Google Ads API version (avoid deprecated defaults)."""
    return client.get_service(service_name, version=settings.google_ads_api_version)


def _get_type(client, type_name: str):
    """Always use configured Google Ads API version for message types."""
    return client.get_type(type_name, version=settings.google_ads_api_version)


class GoogleAdsService:
    def __init__(self, repo: GoogleAdsRepository):
        self.repo = repo

    # ── Accounts ─────────────────────────────────────────────────────────────

    async def list_accounts(self, refresh_token: str) -> list[str]:
        client = _get_client(refresh_token)
        service = _get_service(client, "CustomerService")
        result = service.list_accessible_customers()
        return list(result.resource_names)

    # ── Budget ────────────────────────────────────────────────────────────────

    async def create_budget(self, customer_id: str, name: str, amount_inr: int,
                            delivery_method: str, refresh_token: str) -> dict:
        client = _get_client(refresh_token)
        service = _get_service(client, "CampaignBudgetService")
        operation = _get_type(client, "CampaignBudgetOperation")
        budget = operation.create

        unique_name = f"{name} {uuid.uuid4()}"
        budget.name = unique_name
        budget.amount_micros = amount_inr * 1_000_000
        budget.delivery_method = getattr(
            client.enums.BudgetDeliveryMethodEnum, delivery_method
        )

        response = service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[operation]
        )
        resource_name = response.results[0].resource_name

        db_id = await self.repo.save_budget(
            customer_id=customer_id,
            name=unique_name,
            amount_inr=amount_inr,
            delivery_method=delivery_method,
            resource_name=resource_name,
        )
        return {"status": "created", "budget_resource": resource_name, "db_id": db_id}

    # ── Campaign ──────────────────────────────────────────────────────────────

    async def create_campaign(self, customer_id: str, name: str, budget_resource: str,
                              channel_type: str, status: str, refresh_token: str) -> dict:
        client = _get_client(refresh_token)
        service = _get_service(client, "CampaignService")
        operation = _get_type(client, "CampaignOperation")
        campaign = operation.create

        unique_name = f"{name} {uuid.uuid4()}"
        campaign.name = unique_name
        campaign.campaign_budget = budget_resource
        campaign.advertising_channel_type = getattr(
            client.enums.AdvertisingChannelTypeEnum, channel_type
        )
        campaign.status = getattr(client.enums.CampaignStatusEnum, status)
        campaign.manual_cpc.enhanced_cpc_enabled = False
        campaign.contains_eu_political_advertising = (
            client.enums.EuPoliticalAdvertisingStatusEnum
            .DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
        )

        response = service.mutate_campaigns(
            customer_id=customer_id, operations=[operation]
        )
        resource_name = response.results[0].resource_name

        db_id = await self.repo.save_campaign(
            customer_id=customer_id,
            name=unique_name,
            budget_resource=budget_resource,
            channel_type=channel_type,
            status=status,
            resource_name=resource_name,
        )
        return {"status": "created", "campaign_resource": resource_name, "db_id": db_id}

    async def list_campaigns(self, customer_id: str, refresh_token: str) -> list[dict]:
        client = _get_client(refresh_token)
        ga_service = _get_service(client, "GoogleAdsService")
        query = """
            SELECT campaign.id, campaign.name, campaign.status
            FROM campaign
            ORDER BY campaign.id
        """
        response = ga_service.search(customer_id=customer_id, query=query)
        return [
            {
                "id": row.campaign.id,
                "name": row.campaign.name,
                "status": row.campaign.status.name,
                "resource": f"customers/{customer_id}/campaigns/{row.campaign.id}",
            }
            for row in response
        ]

    async def update_campaign_status(self, customer_id: str, campaign_id: str,
                                     status: str, refresh_token: str) -> dict:
        client = _get_client(refresh_token)
        service = _get_service(client, "CampaignService")
        operation = _get_type(client, "CampaignOperation")
        campaign = operation.update

        campaign.resource_name = f"customers/{customer_id}/campaigns/{campaign_id}"
        campaign.status = getattr(client.enums.CampaignStatusEnum, status.upper())

        from google.protobuf import field_mask_pb2
        operation.update_mask.CopyFrom(
            field_mask_pb2.FieldMask(paths=["status"])
        )

        service.mutate_campaigns(customer_id=customer_id, operations=[operation])
        return {"status": "updated", "campaign_id": campaign_id, "new_status": status.upper()}

    async def delete_campaign(self, customer_id: str, campaign_id: str,
                              refresh_token: str) -> dict:
        client = _get_client(refresh_token)
        service = _get_service(client, "CampaignService")
        operation = _get_type(client, "CampaignOperation")
        operation.remove = f"customers/{customer_id}/campaigns/{campaign_id}"

        service.mutate_campaigns(customer_id=customer_id, operations=[operation])

        await self.repo.save_deleted_campaign(customer_id, campaign_id)
        return {"status": "deleted", "campaign_id": campaign_id}

    # ── Metrics ───────────────────────────────────────────────────────────────

    async def fetch_metrics(self, customer_id: str, refresh_token: str,
                            days: int = 30) -> list[dict]:
        client = _get_client(refresh_token)
        ga_service = _get_service(client, "GoogleAdsService")

        end = date.today()
        start = end - timedelta(days=days)

        query = f"""
            SELECT
              campaign.id,
              campaign.name,
              campaign.status,
              metrics.clicks,
              metrics.impressions,
              metrics.cost_micros,
              metrics.conversions,
              metrics.ctr
            FROM campaign
            WHERE segments.date BETWEEN '{start}' AND '{end}'
              AND campaign.status != 'REMOVED'
            ORDER BY campaign.id
        """
        response = ga_service.search(customer_id=customer_id, query=query)
        metrics = []
        for row in response:
            cost_inr = row.metrics.cost_micros / 1_000_000
            metrics.append({
                "campaign_id": row.campaign.id,
                "campaign_name": row.campaign.name,
                "campaign_status": row.campaign.status.name,
                "clicks": row.metrics.clicks,
                "impressions": row.metrics.impressions,
                "cost_inr": round(cost_inr, 2),
                "conversions": row.metrics.conversions,
                "ctr": round(row.metrics.ctr, 4),
            })

        await self.repo.save_metrics(customer_id=customer_id, metrics=metrics)
        return metrics

    async def get_dashboard_stats(self, customer_id: str, refresh_token: str) -> dict:
        metrics = await self.repo.get_latest_metrics(customer_id)
        campaigns = await self.list_campaigns(customer_id, refresh_token)
        active = sum(1 for c in campaigns if c["status"] == "ENABLED")
        paused = sum(1 for c in campaigns if c["status"] == "PAUSED")

        total_clicks = sum(m.get("clicks", 0) for m in metrics)
        total_impressions = sum(m.get("impressions", 0) for m in metrics)
        total_cost = sum(m.get("cost_inr", 0.0) for m in metrics)
        total_conversions = sum(m.get("conversions", 0.0) for m in metrics)
        avg_ctr = (
            round(sum(m.get("ctr", 0.0) for m in metrics) / len(metrics), 4)
            if metrics else 0.0
        )

        return {
            "total_clicks": total_clicks,
            "total_impressions": total_impressions,
            "total_cost_inr": round(total_cost, 2),
            "total_conversions": round(total_conversions, 2),
            "avg_ctr": avg_ctr,
            "campaign_count": len(campaigns),
            "active_campaigns": active,
            "paused_campaigns": paused,
        }

    # ── Ad Group ──────────────────────────────────────────────────────────────

    async def create_adgroup(self, customer_id: str, name: str, campaign_resource: str,
                             cpc_bid_inr: int, type_: str, status: str,
                             refresh_token: str) -> dict:
        client = _get_client(refresh_token)
        service = _get_service(client, "AdGroupService")
        operation = _get_type(client, "AdGroupOperation")
        ad_group = operation.create

        unique_name = f"{name} {uuid.uuid4()}"
        ad_group.name = unique_name
        ad_group.campaign = campaign_resource
        ad_group.type_ = getattr(client.enums.AdGroupTypeEnum, type_)
        ad_group.status = getattr(client.enums.AdGroupStatusEnum, status)
        ad_group.cpc_bid_micros = cpc_bid_inr * 1_000_000

        response = service.mutate_ad_groups(
            customer_id=customer_id, operations=[operation]
        )
        resource_name = response.results[0].resource_name

        db_id = await self.repo.save_adgroup(
            customer_id=customer_id,
            name=unique_name,
            campaign_resource=campaign_resource,
            type_=type_,
            status=status,
            cpc_bid_inr=cpc_bid_inr,
            resource_name=resource_name,
        )
        return {"status": "created", "ad_group_resource": resource_name, "db_id": db_id}

    # ── Ad ────────────────────────────────────────────────────────────────────

    async def create_ad(self, customer_id: str, ad_group_resource: str, final_url: str,
                        headlines: list[str], descriptions: list[str], status: str,
                        refresh_token: str) -> dict:
        client = _get_client(refresh_token)
        service = _get_service(client, "AdGroupAdService")
        operation = _get_type(client, "AdGroupAdOperation")
        ad_group_ad = operation.create

        ad_group_ad.ad_group = ad_group_resource
        ad = ad_group_ad.ad
        ad.final_urls.append(final_url)

        rsa = ad.responsive_search_ad
        for text in headlines:
            h = _get_type(client, "AdTextAsset")
            h.text = text
            rsa.headlines.append(h)
        for text in descriptions:
            d = _get_type(client, "AdTextAsset")
            d.text = text
            rsa.descriptions.append(d)

        ad_group_ad.status = getattr(client.enums.AdGroupAdStatusEnum, status)

        response = service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[operation]
        )
        resource_name = response.results[0].resource_name

        db_id = await self.repo.save_ad(
            customer_id=customer_id,
            ad_group_resource=ad_group_resource,
            final_url=final_url,
            headlines=headlines,
            descriptions=descriptions,
            status=status,
            resource_name=resource_name,
        )
        return {"status": "created", "ad_resource": resource_name, "db_id": db_id}

    # ── Keywords ──────────────────────────────────────────────────────────────

    async def add_keywords(self, customer_id: str, ad_group_resource: str,
                           keywords: list[str], match_type: str,
                           refresh_token: str) -> dict:
        client = _get_client(refresh_token)
        service = _get_service(client, "AdGroupCriterionService")
        operations = []

        for keyword_text in keywords:
            operation = _get_type(client, "AdGroupCriterionOperation")
            criterion = operation.create
            criterion.ad_group = ad_group_resource
            criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
            criterion.keyword.text = keyword_text
            criterion.keyword.match_type = getattr(
                client.enums.KeywordMatchTypeEnum, match_type
            )
            operations.append(operation)

        response = service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=operations
        )
        added_resources = [r.resource_name for r in response.results]

        db_id = await self.repo.save_keywords(
            customer_id=customer_id,
            ad_group_resource=ad_group_resource,
            keywords=keywords,
            match_type=match_type,
            resource_names=added_resources,
        )
        return {"status": "added", "keywords_added": added_resources, "db_id": db_id}
