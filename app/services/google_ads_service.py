"""Google Ads API service — wraps the google-ads SDK."""

import uuid

from app.repositories.google_ads import GoogleAdsRepository


def _get_client():
    """Load Google Ads client from google-ads.yaml."""
    from google.ads.googleads.client import GoogleAdsClient
    return GoogleAdsClient.load_from_storage("google-ads.yaml")


class GoogleAdsService:
    def __init__(self, repo: GoogleAdsRepository):
        self.repo = repo

    # ── Accounts ─────────────────────────────────────────────────────────────

    async def list_accounts(self) -> list[str]:
        client = _get_client()
        service = client.get_service("CustomerService")
        result = service.list_accessible_customers()
        return list(result.resource_names)

    # ── Budget ────────────────────────────────────────────────────────────────

    async def create_budget(self, customer_id: str, name: str, amount_inr: int,
                            delivery_method: str) -> dict:
        client = _get_client()
        service = client.get_service("CampaignBudgetService")
        operation = client.get_type("CampaignBudgetOperation")
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
                              channel_type: str, status: str) -> dict:
        client = _get_client()
        service = client.get_service("CampaignService")
        operation = client.get_type("CampaignOperation")
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

    async def list_campaigns(self, customer_id: str) -> list[dict]:
        client = _get_client()
        ga_service = client.get_service("GoogleAdsService")
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

    async def delete_campaign(self, customer_id: str, campaign_id: str) -> dict:
        client = _get_client()
        service = client.get_service("CampaignService")
        operation = client.get_type("CampaignOperation")
        operation.remove = f"customers/{customer_id}/campaigns/{campaign_id}"

        service.mutate_campaigns(customer_id=customer_id, operations=[operation])

        await self.repo.save_deleted_campaign(customer_id, campaign_id)
        return {"status": "deleted", "campaign_id": campaign_id}

    # ── Ad Group ──────────────────────────────────────────────────────────────

    async def create_adgroup(self, customer_id: str, name: str, campaign_resource: str,
                             cpc_bid_inr: int, type_: str, status: str) -> dict:
        client = _get_client()
        service = client.get_service("AdGroupService")
        operation = client.get_type("AdGroupOperation")
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
                        headlines: list[str], descriptions: list[str], status: str) -> dict:
        client = _get_client()
        service = client.get_service("AdGroupAdService")
        operation = client.get_type("AdGroupAdOperation")
        ad_group_ad = operation.create

        ad_group_ad.ad_group = ad_group_resource
        ad = ad_group_ad.ad
        ad.final_urls.append(final_url)

        rsa = ad.responsive_search_ad
        for text in headlines:
            h = client.get_type("AdTextAsset")
            h.text = text
            rsa.headlines.append(h)
        for text in descriptions:
            d = client.get_type("AdTextAsset")
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
                           keywords: list[str], match_type: str) -> dict:
        client = _get_client()
        service = client.get_service("AdGroupCriterionService")
        operations = []

        for keyword_text in keywords:
            operation = client.get_type("AdGroupCriterionOperation")
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
