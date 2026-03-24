"""Google Ads API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.deps import get_current_user
from app.database import get_database
from app.repositories.google_ads import GoogleAdsRepository
from app.schemas.google_ads import (
    AccountsResponse,
    AdCreateRequest,
    AdGroupCreateRequest,
    AdGroupResponse,
    AdResponse,
    BudgetCreateRequest,
    BudgetResponse,
    CampaignCreateRequest,
    CampaignResponse,
    CampaignsListResponse,
    KeywordsAddRequest,
    KeywordsResponse,
)
from app.services.google_ads_service import GoogleAdsService

router = APIRouter()


# ─── Dependencies ─────────────────────────────────────────────────────────────

async def get_ads_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> GoogleAdsService:
    repo = GoogleAdsRepository(db)
    return GoogleAdsService(repo)


async def get_ads_repo(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> GoogleAdsRepository:
    return GoogleAdsRepository(db)


# ─── Accounts ─────────────────────────────────────────────────────────────────

@router.get(
    "/accounts",
    response_model=AccountsResponse,
    summary="List all accessible Google Ads accounts",
)
async def list_accounts(
    _: Annotated[dict, Depends(get_current_user)],
    service: Annotated[GoogleAdsService, Depends(get_ads_service)],
):
    try:
        accounts = await service.list_accounts()
        return {"accounts": accounts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Budget ───────────────────────────────────────────────────────────────────

@router.post(
    "/budget",
    response_model=BudgetResponse,
    summary="Create a campaign budget",
    description=(
        "Creates a Google Ads campaign budget and saves it to MongoDB.\n\n"
        "- **delivery_method**: `STANDARD` (spend evenly) or `ACCELERATED` (spend as fast as possible)\n"
        "- **amount_inr**: budget in INR — auto-converted to micros"
    ),
)
async def create_budget(
    req: BudgetCreateRequest,
    customer_id: str = Query(..., description="Your Google Ads account ID (no dashes)"),
    _: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[GoogleAdsService, Depends(get_ads_service)] = None,
):
    try:
        return await service.create_budget(
            customer_id=customer_id,
            name=req.name,
            amount_inr=req.amount_inr,
            delivery_method=req.delivery_method,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budgets", summary="List all budgets stored in MongoDB")
async def get_budgets(
    _: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[GoogleAdsRepository, Depends(get_ads_repo)],
):
    return {"budgets": await repo.get_budgets()}


# ─── Campaign ─────────────────────────────────────────────────────────────────

@router.post(
    "/campaign",
    response_model=CampaignResponse,
    summary="Create a campaign",
    description=(
        "Creates a Google Ads campaign and saves it to MongoDB.\n\n"
        "- **channel_type**: `SEARCH`, `DISPLAY`, `VIDEO`, `SHOPPING`\n"
        "- **status**: `ENABLED` or `PAUSED`\n"
        "- **budget_resource**: resource name from POST /budget response"
    ),
)
async def create_campaign(
    req: CampaignCreateRequest,
    customer_id: str = Query(..., description="Your Google Ads account ID (no dashes)"),
    _: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[GoogleAdsService, Depends(get_ads_service)] = None,
):
    try:
        return await service.create_campaign(
            customer_id=customer_id,
            name=req.name,
            budget_resource=req.budget_resource,
            channel_type=req.channel_type,
            status=req.status,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/campaigns/live",
    response_model=CampaignsListResponse,
    summary="List all campaigns live from Google Ads",
)
async def list_campaigns_live(
    customer_id: str = Query(..., description="Your Google Ads account ID (no dashes)"),
    _: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[GoogleAdsService, Depends(get_ads_service)] = None,
):
    try:
        campaigns = await service.list_campaigns(customer_id)
        return {"campaigns": campaigns, "count": len(campaigns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns", summary="List all campaigns stored in MongoDB")
async def get_campaigns(
    _: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[GoogleAdsRepository, Depends(get_ads_repo)],
):
    return {"campaigns": await repo.get_campaigns()}


@router.delete(
    "/campaign/{campaign_id}",
    summary="Delete a campaign",
)
async def delete_campaign(
    campaign_id: str,
    customer_id: str = Query(..., description="Your Google Ads account ID (no dashes)"),
    _: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[GoogleAdsService, Depends(get_ads_service)] = None,
):
    try:
        return await service.delete_campaign(customer_id, campaign_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Ad Group ─────────────────────────────────────────────────────────────────

@router.post(
    "/adgroup",
    response_model=AdGroupResponse,
    summary="Create an ad group",
    description=(
        "Creates an ad group under a campaign and saves to MongoDB.\n\n"
        "- **type_**: `SEARCH_STANDARD` (only valid for SEARCH campaigns)\n"
        "- **cpc_bid_inr**: cost-per-click bid in INR\n"
        "- **campaign_resource**: resource name from POST /campaign response"
    ),
)
async def create_adgroup(
    req: AdGroupCreateRequest,
    customer_id: str = Query(..., description="Your Google Ads account ID (no dashes)"),
    _: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[GoogleAdsService, Depends(get_ads_service)] = None,
):
    try:
        return await service.create_adgroup(
            customer_id=customer_id,
            name=req.name,
            campaign_resource=req.campaign_resource,
            cpc_bid_inr=req.cpc_bid_inr,
            type_=req.type_,
            status=req.status,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/adgroups", summary="List all ad groups stored in MongoDB")
async def get_adgroups(
    _: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[GoogleAdsRepository, Depends(get_ads_repo)],
):
    return {"adgroups": await repo.get_adgroups()}


# ─── Ad ───────────────────────────────────────────────────────────────────────

@router.post(
    "/ad",
    response_model=AdResponse,
    summary="Create a Responsive Search Ad",
    description=(
        "Creates a Responsive Search Ad and saves to MongoDB.\n\n"
        "- **headlines**: minimum 3, max 30 chars each\n"
        "- **descriptions**: minimum 2, max 90 chars each\n"
        "- **ad_group_resource**: resource name from POST /adgroup response"
    ),
)
async def create_ad(
    req: AdCreateRequest,
    customer_id: str = Query(..., description="Your Google Ads account ID (no dashes)"),
    _: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[GoogleAdsService, Depends(get_ads_service)] = None,
):
    try:
        return await service.create_ad(
            customer_id=customer_id,
            ad_group_resource=req.ad_group_resource,
            final_url=req.final_url,
            headlines=req.headlines,
            descriptions=req.descriptions,
            status=req.status,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ads", summary="List all ads stored in MongoDB")
async def get_ads(
    _: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[GoogleAdsRepository, Depends(get_ads_repo)],
):
    return {"ads": await repo.get_ads()}


# ─── Keywords ─────────────────────────────────────────────────────────────────

@router.post(
    "/keywords",
    response_model=KeywordsResponse,
    summary="Add keywords to an ad group",
    description=(
        "Adds keywords to an ad group and saves to MongoDB.\n\n"
        "- **match_type**: `BROAD`, `PHRASE`, or `EXACT`\n"
        "- **ad_group_resource**: resource name from POST /adgroup response"
    ),
)
async def add_keywords(
    req: KeywordsAddRequest,
    customer_id: str = Query(..., description="Your Google Ads account ID (no dashes)"),
    _: Annotated[dict, Depends(get_current_user)] = None,
    service: Annotated[GoogleAdsService, Depends(get_ads_service)] = None,
):
    try:
        return await service.add_keywords(
            customer_id=customer_id,
            ad_group_resource=req.ad_group_resource,
            keywords=req.keywords,
            match_type=req.match_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keywords", summary="List all keywords stored in MongoDB")
async def get_keywords(
    _: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[GoogleAdsRepository, Depends(get_ads_repo)],
):
    return {"keywords": await repo.get_keywords()}
