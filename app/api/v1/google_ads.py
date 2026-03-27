"""Google Ads API endpoints."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.core.deps import get_current_user
from app.database import get_database
from app.repositories.google_ads import GoogleAdsRepository
from app.repositories.google_ads_connection import GoogleAdsConnectionRepository
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
    CampaignStatusUpdateRequest,
    CampaignsListResponse,
    ConnectionStatus,
    DashboardStats,
    InsightsResponse,
    KeywordsAddRequest,
    KeywordsResponse,
    MetricsResponse,
    OAuthUrlResponse,
)
from app.services.google_ads_oauth import exchange_code_for_tokens, get_oauth_url
from app.services.google_ads_service import GoogleAdsService
from app.services.ai_insights import generate_insights

router = APIRouter()

# Must match Authorized redirect URI registered in Google Cloud Console for client 88315194725-...
GOOGLE_ADS_REDIRECT_URI = settings.google_ads_redirect_uri


# ─── Dependencies ─────────────────────────────────────────────────────────────

async def get_ads_service(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> GoogleAdsService:
    return GoogleAdsService(GoogleAdsRepository(db))


async def get_ads_repo(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> GoogleAdsRepository:
    return GoogleAdsRepository(db)


async def get_connection_repo(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> GoogleAdsConnectionRepository:
    return GoogleAdsConnectionRepository(db)


async def require_ads_connection(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> str:
    """
    Dependency that returns the current user's stored Google Ads refresh_token.
    Raises 403 if the user has not connected their Google Ads account yet.
    """
    conn_repo = GoogleAdsConnectionRepository(db)
    connection = await conn_repo.get_connection(str(user.get("id") or user.get("_id")))
    if not connection or not connection.get("refresh_token"):
        raise HTTPException(
            status_code=403,
            detail="Google Ads account not connected. Call GET /google-ads/oauth/url first.",
        )
    return connection["refresh_token"]


# ─── OAuth — Connect Google Ads Account ───────────────────────────────────────

@router.get(
    "/oauth/url",
    response_model=OAuthUrlResponse,
    summary="Get Google OAuth URL to connect your Google Ads account",
    description=(
        "Returns a Google authorization URL. Open it in a browser, "
        "grant access, and the system will store your refresh token automatically."
    ),
    tags=["google-ads-connect"],
)
async def get_connect_url(
    user: Annotated[dict, Depends(get_current_user)],
):
    user_id = str(user.get("id") or user.get("_id"))
    url = get_oauth_url(state=user_id, redirect_uri=GOOGLE_ADS_REDIRECT_URI)
    return {"url": url}


@router.get(
    "/oauth/callback",
    response_class=HTMLResponse,
    summary="OAuth callback — stores refresh token (opened by Google redirect)",
    include_in_schema=False,
)
async def oauth_callback(
    request: Request,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    code: str = Query(None),
    state: str = Query(None),   # user_id passed as state
    error: str = Query(None),
):
    if error:
        return HTMLResponse(
            content=f"<h2>Connection failed</h2><p>{error}</p>",
            status_code=400,
        )
    if not code or not state:
        return HTMLResponse(
            content="<h2>Invalid callback</h2><p>Missing code or state.</p>",
            status_code=400,
        )

    try:
        tokens = await exchange_code_for_tokens(
            code=code, redirect_uri=GOOGLE_ADS_REDIRECT_URI
        )
        refresh_token = tokens.get("refresh_token")
        if not refresh_token:
            return HTMLResponse(
                content="<h2>Error</h2><p>No refresh token returned. Make sure you have not already authorized this app — try revoking access at myaccount.google.com/permissions and reconnecting.</p>",
                status_code=400,
            )

        conn_repo = GoogleAdsConnectionRepository(db)

        # Try to resolve org_id from the user document
        from bson import ObjectId
        org_id = None
        try:
            user_doc = await db["users"].find_one({"_id": ObjectId(state)})
            if user_doc:
                org_id = user_doc.get("organization_id")
        except Exception:
            pass

        await conn_repo.save_connection(
            user_id=state,
            org_id=org_id,
            refresh_token=refresh_token,
            token_payload=tokens,
        )

        return HTMLResponse(content="""
            <html><body style="font-family:sans-serif;text-align:center;padding:60px">
              <h2 style="color:green">✅ Google Ads Connected!</h2>
              <p>Your account has been linked. You can close this tab and return to the app.</p>
            </body></html>
        """)
    except Exception as e:
        return HTMLResponse(
            content=f"<h2>Error</h2><p>{e}</p>",
            status_code=500,
        )


@router.get(
    "/connection",
    response_model=ConnectionStatus,
    summary="Check if your Google Ads account is connected",
    tags=["google-ads-connect"],
)
async def get_connection_status(
    user: Annotated[dict, Depends(get_current_user)],
    conn_repo: Annotated[GoogleAdsConnectionRepository, Depends(get_connection_repo)],
):
    connection = await conn_repo.get_connection(str(user.get("id") or user.get("_id")))
    if not connection:
        return {"connected": False}
    connected_at = connection.get("connected_at", "")
    if hasattr(connected_at, "isoformat"):
        connected_at = connected_at.isoformat()
    return {"connected": True, "connected_at": str(connected_at)}


@router.delete(
    "/connection",
    summary="Disconnect your Google Ads account",
    tags=["google-ads-connect"],
)
async def disconnect(
    user: Annotated[dict, Depends(get_current_user)],
    conn_repo: Annotated[GoogleAdsConnectionRepository, Depends(get_connection_repo)],
):
    deleted = await conn_repo.delete_connection(str(user.get("id") or user.get("_id")))
    if not deleted:
        raise HTTPException(status_code=404, detail="No connection found.")
    return {"status": "disconnected"}


# ─── Accounts ─────────────────────────────────────────────────────────────────

@router.get(
    "/accounts",
    response_model=AccountsResponse,
    summary="List all accessible Google Ads accounts",
)
async def list_accounts(
    user: Annotated[dict, Depends(get_current_user)],
    refresh_token: Annotated[str, Depends(require_ads_connection)],
    service: Annotated[GoogleAdsService, Depends(get_ads_service)],
    repo: Annotated[GoogleAdsRepository, Depends(get_ads_repo)],
):
    try:
        accounts = await service.list_accounts(refresh_token)
        user_id = str(user.get("id") or user.get("_id"))
        await repo.save_accessible_accounts(user_id=user_id, customer_resource_names=accounts)
        return {"accounts": accounts}
    except Exception as e:
        message = str(e)
        if "target method can't be resolved" in message:
            raise HTTPException(
                status_code=502,
                detail=(
                    "Google Ads API method resolution failed. This is usually caused by an outdated "
                    "google-ads SDK/API version mismatch. Upgrade the google-ads package and retry."
                ),
            )
        raise HTTPException(status_code=500, detail=message)


# ─── Dashboard ────────────────────────────────────────────────────────────────

@router.get(
    "/dashboard",
    response_model=DashboardStats,
    summary="Get aggregated dashboard stats for a Google Ads account",
)
async def get_dashboard(
    customer_id: str = Query(..., description="Google Ads account ID (no dashes)"),
    refresh_token: str = Depends(require_ads_connection),
    service: GoogleAdsService = Depends(get_ads_service),
):
    try:
        return await service.get_dashboard_stats(customer_id, refresh_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Metrics ──────────────────────────────────────────────────────────────────

@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Fetch campaign performance metrics (last N days)",
)
async def get_metrics(
    customer_id: str = Query(...),
    days: int = Query(30, ge=1, le=90),
    refresh_token: str = Depends(require_ads_connection),
    service: GoogleAdsService = Depends(get_ads_service),
):
    try:
        metrics = await service.fetch_metrics(customer_id, refresh_token, days)
        return {"metrics": metrics, "count": len(metrics)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── AI Insights ──────────────────────────────────────────────────────────────

@router.post(
    "/insights/generate",
    response_model=InsightsResponse,
    summary="Generate AI insights from latest metrics",
)
async def generate_ai_insights(
    customer_id: str = Query(...),
    refresh_token: str = Depends(require_ads_connection),
    service: GoogleAdsService = Depends(get_ads_service),
    repo: GoogleAdsRepository = Depends(get_ads_repo),
):
    try:
        metrics = await repo.get_latest_metrics(customer_id)
        if not metrics:
            metrics = await service.fetch_metrics(customer_id, refresh_token, days=30)

        insights = generate_insights(metrics)
        generated_at = datetime.now(timezone.utc).isoformat()
        await repo.save_insights(customer_id=customer_id, insights=insights)

        return {"insights": insights, "count": len(insights), "generated_at": generated_at}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/insights",
    response_model=InsightsResponse,
    summary="Get latest saved AI insights",
)
async def get_insights(
    customer_id: str = Query(...),
    _: str = Depends(require_ads_connection),
    repo: GoogleAdsRepository = Depends(get_ads_repo),
):
    try:
        doc = await repo.get_latest_insights(customer_id)
        if not doc:
            return {"insights": [], "count": 0, "generated_at": ""}
        insights = doc.get("insights", [])
        created_at = doc.get("created_at", "")
        if hasattr(created_at, "isoformat"):
            created_at = created_at.isoformat()
        return {"insights": insights, "count": len(insights), "generated_at": str(created_at)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Budget ───────────────────────────────────────────────────────────────────

@router.post("/budget", response_model=BudgetResponse, summary="Create a campaign budget")
async def create_budget(
    req: BudgetCreateRequest,
    customer_id: str = Query(...),
    refresh_token: str = Depends(require_ads_connection),
    service: GoogleAdsService = Depends(get_ads_service),
):
    try:
        return await service.create_budget(
            customer_id=customer_id,
            name=req.name,
            amount_inr=req.amount_inr,
            delivery_method=req.delivery_method,
            refresh_token=refresh_token,
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

@router.post("/campaign", response_model=CampaignResponse, summary="Create a campaign")
async def create_campaign(
    req: CampaignCreateRequest,
    customer_id: str = Query(...),
    refresh_token: str = Depends(require_ads_connection),
    service: GoogleAdsService = Depends(get_ads_service),
):
    try:
        return await service.create_campaign(
            customer_id=customer_id,
            name=req.name,
            budget_resource=req.budget_resource,
            channel_type=req.channel_type,
            status=req.status,
            refresh_token=refresh_token,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/campaign/{campaign_id}/status",
    summary="Pause or enable a campaign",
)
async def update_campaign_status(
    campaign_id: str,
    req: CampaignStatusUpdateRequest,
    customer_id: str = Query(...),
    refresh_token: str = Depends(require_ads_connection),
    service: GoogleAdsService = Depends(get_ads_service),
):
    try:
        return await service.update_campaign_status(
            customer_id=customer_id,
            campaign_id=campaign_id,
            status=req.status,
            refresh_token=refresh_token,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/live", response_model=CampaignsListResponse,
            summary="List campaigns live from Google Ads")
async def list_campaigns_live(
    customer_id: str = Query(...),
    refresh_token: str = Depends(require_ads_connection),
    service: GoogleAdsService = Depends(get_ads_service),
):
    try:
        campaigns = await service.list_campaigns(customer_id, refresh_token)
        return {"campaigns": campaigns, "count": len(campaigns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns", summary="List all campaigns stored in MongoDB")
async def get_campaigns(
    _: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[GoogleAdsRepository, Depends(get_ads_repo)],
):
    return {"campaigns": await repo.get_campaigns()}


@router.delete("/campaign/{campaign_id}", summary="Delete a campaign")
async def delete_campaign(
    campaign_id: str,
    customer_id: str = Query(...),
    refresh_token: str = Depends(require_ads_connection),
    service: GoogleAdsService = Depends(get_ads_service),
):
    try:
        return await service.delete_campaign(customer_id, campaign_id, refresh_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Ad Group ─────────────────────────────────────────────────────────────────

@router.post("/adgroup", response_model=AdGroupResponse, summary="Create an ad group")
async def create_adgroup(
    req: AdGroupCreateRequest,
    customer_id: str = Query(...),
    refresh_token: str = Depends(require_ads_connection),
    service: GoogleAdsService = Depends(get_ads_service),
):
    try:
        return await service.create_adgroup(
            customer_id=customer_id,
            name=req.name,
            campaign_resource=req.campaign_resource,
            cpc_bid_inr=req.cpc_bid_inr,
            type_=req.type_,
            status=req.status,
            refresh_token=refresh_token,
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

@router.post("/ad", response_model=AdResponse, summary="Create a Responsive Search Ad")
async def create_ad(
    req: AdCreateRequest,
    customer_id: str = Query(...),
    refresh_token: str = Depends(require_ads_connection),
    service: GoogleAdsService = Depends(get_ads_service),
):
    try:
        return await service.create_ad(
            customer_id=customer_id,
            ad_group_resource=req.ad_group_resource,
            final_url=req.final_url,
            headlines=req.headlines,
            descriptions=req.descriptions,
            status=req.status,
            refresh_token=refresh_token,
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

@router.post("/keywords", response_model=KeywordsResponse, summary="Add keywords to an ad group")
async def add_keywords(
    req: KeywordsAddRequest,
    customer_id: str = Query(...),
    refresh_token: str = Depends(require_ads_connection),
    service: GoogleAdsService = Depends(get_ads_service),
):
    try:
        return await service.add_keywords(
            customer_id=customer_id,
            ad_group_resource=req.ad_group_resource,
            keywords=req.keywords,
            match_type=req.match_type,
            refresh_token=refresh_token,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keywords", summary="List all keywords stored in MongoDB")
async def get_keywords(
    _: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[GoogleAdsRepository, Depends(get_ads_repo)],
):
    return {"keywords": await repo.get_keywords()}
