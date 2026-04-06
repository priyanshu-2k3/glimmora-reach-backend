"""Meta (Facebook) Ads API endpoints."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.core.deps import get_current_user
from app.database import get_database
from app.repositories.meta_ads import MetaAdsRepository
from app.repositories.meta_ads_connection import MetaAdsConnectionRepository
from app.schemas.meta_ads import (
    AccountInsightsInput,
    AdCreate,
    AdSetCreate,
    AdSetUpdate,
    AdUpdate,
    AudienceCreate,
    CampaignCreate,
    CampaignUpdate,
    ConnectionStatus,
    InsightsInput,
    LeadFormCreate,
    LinkCreativeInput,
    OAuthUrlResponse,
    VideoCreativeInput,
    VideoUploadInput,
)
from app.services import meta_ads_service as meta_svc

router = APIRouter()


# ─── Dependencies ────────────────────────────────────────────────────────────

async def get_meta_repo(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> MetaAdsRepository:
    return MetaAdsRepository(db)


async def get_connection_repo(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> MetaAdsConnectionRepository:
    return MetaAdsConnectionRepository(db)


async def require_meta_connection(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> str:
    """Return the user's stored Meta long-lived access token. Raises 403 if not connected."""
    conn_repo = MetaAdsConnectionRepository(db)
    connection = await conn_repo.get_connection(str(user.get("id") or user.get("_id")))
    if not connection or not connection.get("access_token"):
        raise HTTPException(
            status_code=403,
            detail="Meta Ads account not connected. Call GET /meta-ads/oauth/url first.",
        )
    return connection["access_token"]


async def get_page_token(
    page_id: str,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> str:
    """Look up the Page Access Token for a given page_id from stored connection data.

    Page tokens stored during OAuth (when fetched with a long-lived user token)
    are themselves long-lived (~60 days).
    """
    conn_repo = MetaAdsConnectionRepository(db)
    user_id = str(user.get("id") or user.get("_id"))
    connection = await conn_repo.get_connection(user_id)
    if not connection or not connection.get("access_token"):
        raise HTTPException(status_code=403, detail="Meta Ads account not connected.")

    pages = connection.get("pages") or []
    for page in pages:
        if page.get("id") == page_id:
            return page["access_token"]
    raise HTTPException(
        status_code=404,
        detail=f"Page {page_id} not found in your connected pages. Reconnect your Meta account.",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# OAuth — Connect Meta Ads Account
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/oauth/url",
    response_model=OAuthUrlResponse,
    summary="Get Meta OAuth URL to connect your Meta Ads account",
    tags=["meta-ads-connect"],
)
async def get_connect_url(
    user: Annotated[dict, Depends(get_current_user)],
):
    user_id = str(user.get("id") or user.get("_id"))
    url = meta_svc.build_oauth_url(state=user_id)
    return {"url": url}


@router.get(
    "/oauth/callback",
    response_class=HTMLResponse,
    summary="OAuth callback — exchanges code for long-lived token",
    include_in_schema=False,
)
async def oauth_callback(
    request: Request,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    code: str = Query(None),
    state: str = Query(None),
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
        # Step 1: exchange code for short-lived token
        token_data = await meta_svc.exchange_code_for_token(code)
        short_token = token_data.get("access_token")
        if not short_token:
            detail = token_data.get("error", {}).get("message", "Unknown error")
            return HTMLResponse(
                content=f"<h2>Error</h2><p>Token exchange failed: {detail}</p>",
                status_code=400,
            )

        # Step 2: exchange for long-lived token (~60 days)
        long_token_data = await meta_svc.exchange_long_lived_token(short_token)
        access_token = long_token_data.get("access_token")
        if not access_token:
            detail = long_token_data.get("error", {}).get("message", "Unknown error")
            return HTMLResponse(
                content=f"<h2>Error</h2><p>Long-lived token exchange failed: {detail}</p>",
                status_code=400,
            )

        # Step 3: fetch ad accounts and pages (long-lived user token yields long-lived page tokens)
        ad_accounts = await meta_svc.get_ad_accounts(access_token)
        pages = await meta_svc.get_pages(access_token)

        # Step 4: resolve org_id from user document
        from bson import ObjectId
        org_id = None
        try:
            user_doc = await db["users"].find_one({"_id": ObjectId(state)})
            if user_doc:
                org_id = user_doc.get("organization_id")
        except Exception:
            pass

        # Step 5: persist connection
        conn_repo = MetaAdsConnectionRepository(db)
        await conn_repo.save_connection(
            user_id=state,
            org_id=org_id,
            access_token=access_token,
            token_payload={
                "token_type": long_token_data.get("token_type", "bearer"),
                "expires_in": long_token_data.get("expires_in"),
                "ad_accounts": ad_accounts.get("data"),
                "pages": pages.get("data"),
            },
        )

        return HTMLResponse(content="""
            <html><body style="font-family:sans-serif;text-align:center;padding:60px">
              <h2 style="color:green">Meta Ads Connected!</h2>
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
    summary="Check if your Meta Ads account is connected",
    tags=["meta-ads-connect"],
)
async def get_connection_status(
    user: Annotated[dict, Depends(get_current_user)],
    conn_repo: Annotated[MetaAdsConnectionRepository, Depends(get_connection_repo)],
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
    summary="Disconnect your Meta Ads account",
    tags=["meta-ads-connect"],
)
async def disconnect(
    user: Annotated[dict, Depends(get_current_user)],
    conn_repo: Annotated[MetaAdsConnectionRepository, Depends(get_connection_repo)],
):
    deleted = await conn_repo.delete_connection(str(user.get("id") or user.get("_id")))
    if not deleted:
        raise HTTPException(status_code=404, detail="No connection found.")
    return {"status": "disconnected"}


# ═══════════════════════════════════════════════════════════════════════════════
# Account
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/account/ad-accounts", summary="List all ad accounts", tags=["meta-ads-account"])
async def ad_accounts(token: Annotated[str, Depends(require_meta_connection)]):
    return await meta_svc.get_ad_accounts(token)


@router.get("/account/pages", summary="List managed Facebook Pages", tags=["meta-ads-account"])
async def pages(token: Annotated[str, Depends(require_meta_connection)]):
    return await meta_svc.get_pages(token)


@router.get("/account/details/{ad_account_id}", summary="Get ad account details", tags=["meta-ads-account"])
async def account_details(
    ad_account_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    return await meta_svc.get_account_details(token, ad_account_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Campaigns
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/campaigns/{ad_account_id}", summary="List campaigns", tags=["meta-ads-campaigns"])
async def list_campaigns(
    ad_account_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
    status_filter: str | None = None,
):
    return await meta_svc.list_campaigns(token, ad_account_id, status_filter)


@router.get("/campaigns/get/{campaign_id}", summary="Get a single campaign", tags=["meta-ads-campaigns"])
async def get_campaign(
    campaign_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    return await meta_svc.get_campaign(token, campaign_id)


@router.post("/campaigns", summary="Create a campaign", tags=["meta-ads-campaigns"])
async def create_campaign(
    body: CampaignCreate,
    token: Annotated[str, Depends(require_meta_connection)],
    user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[MetaAdsRepository, Depends(get_meta_repo)],
):
    payload = {
        "name": body.name,
        "objective": body.objective,
        "status": body.status,
        "special_ad_categories": body.special_ad_categories,
        "is_adset_budget_sharing_enabled": body.is_adset_budget_sharing_enabled,
    }
    if body.daily_budget:
        payload["daily_budget"] = body.daily_budget
    if body.lifetime_budget:
        payload["lifetime_budget"] = body.lifetime_budget
    if body.start_time:
        payload["start_time"] = body.start_time
    if body.stop_time:
        payload["stop_time"] = body.stop_time
    if body.bid_strategy:
        payload["bid_strategy"] = body.bid_strategy

    result = await meta_svc.create_campaign(token, body.ad_account_id, payload)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    user_id = str(user.get("id") or user.get("_id"))
    db_id = await repo.save_campaign(user_id, body.ad_account_id, {
        "meta_id": result.get("id"),
        **payload,
    })
    return {"status": "created", "meta_id": result.get("id"), "db_id": db_id}


@router.patch("/campaigns/{campaign_id}", summary="Update a campaign", tags=["meta-ads-campaigns"])
async def update_campaign(
    campaign_id: str,
    body: CampaignUpdate,
    token: Annotated[str, Depends(require_meta_connection)],
):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await meta_svc.update_campaign(token, campaign_id, fields)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/campaigns/{campaign_id}", summary="Delete a campaign", tags=["meta-ads-campaigns"])
async def delete_campaign(
    campaign_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    result = await meta_svc.delete_campaign(token, campaign_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Ad Sets
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/adsets/{ad_account_id}", summary="List ad sets", tags=["meta-ads-adsets"])
async def list_adsets(
    ad_account_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
    status_filter: str | None = None,
):
    return await meta_svc.list_adsets(token, ad_account_id, status_filter)


@router.get("/adsets/get/{adset_id}", summary="Get a single ad set", tags=["meta-ads-adsets"])
async def get_adset(
    adset_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    return await meta_svc.get_adset(token, adset_id)


@router.post("/adsets", summary="Create an ad set with targeting", tags=["meta-ads-adsets"])
async def create_adset(
    body: AdSetCreate,
    token: Annotated[str, Depends(require_meta_connection)],
    user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[MetaAdsRepository, Depends(get_meta_repo)],
):
    # Build targeting
    targeting: dict = {
        "geo_locations": {"countries": body.countries},
        "age_min": body.age_min,
        "age_max": body.age_max,
    }
    if body.genders:
        targeting["genders"] = body.genders
    if body.publisher_platforms:
        targeting["publisher_platforms"] = body.publisher_platforms
    if body.facebook_positions:
        targeting["facebook_positions"] = body.facebook_positions
    if body.instagram_positions:
        targeting["instagram_positions"] = body.instagram_positions
    if body.device_platforms:
        targeting["device_platforms"] = body.device_platforms
    if body.interests:
        targeting["flexible_spec"] = [{"interests": [{"id": i} for i in body.interests]}]
    if body.behaviors:
        targeting.setdefault("flexible_spec", [{}])[0]["behaviors"] = [
            {"id": b} for b in body.behaviors
        ]
    if body.custom_audiences:
        targeting["custom_audiences"] = [{"id": a} for a in body.custom_audiences]
    if body.excluded_audiences:
        targeting["excluded_custom_audiences"] = [{"id": a} for a in body.excluded_audiences]
    targeting["targeting_automation"] = {"advantage_audience": 0}

    payload: dict = {
        "name": body.name,
        "campaign_id": body.campaign_id,
        "status": body.status,
        "billing_event": body.billing_event,
        "optimization_goal": body.optimization_goal,
        "targeting": targeting,
    }
    if body.bid_strategy:
        payload["bid_strategy"] = body.bid_strategy
    if body.daily_budget:
        payload["daily_budget"] = body.daily_budget
    if body.lifetime_budget:
        payload["lifetime_budget"] = body.lifetime_budget
    if body.bid_amount:
        payload["bid_amount"] = body.bid_amount
    if body.start_time:
        payload["start_time"] = body.start_time
    if body.end_time:
        payload["end_time"] = body.end_time
    if body.promoted_object:
        payload["promoted_object"] = body.promoted_object

    result = await meta_svc.create_adset(token, body.ad_account_id, payload)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    user_id = str(user.get("id") or user.get("_id"))
    db_id = await repo.save_adset(user_id, body.ad_account_id, {
        "meta_id": result.get("id"),
        **payload,
    })
    return {"status": "created", "meta_id": result.get("id"), "db_id": db_id}


@router.patch("/adsets/{adset_id}", summary="Update an ad set", tags=["meta-ads-adsets"])
async def update_adset(
    adset_id: str,
    body: AdSetUpdate,
    token: Annotated[str, Depends(require_meta_connection)],
):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await meta_svc.update_adset(token, adset_id, fields)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/adsets/{adset_id}", summary="Delete an ad set", tags=["meta-ads-adsets"])
async def delete_adset(
    adset_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    result = await meta_svc.delete_adset(token, adset_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Media (Images & Videos)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/media/upload-image", summary="Upload an image", tags=["meta-ads-media"])
async def upload_image(
    token: Annotated[str, Depends(require_meta_connection)],
    user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[MetaAdsRepository, Depends(get_meta_repo)],
    ad_account_id: str = Form(...),
    image: UploadFile = File(...),
):
    result = await meta_svc.upload_image(token, ad_account_id, image)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    user_id = str(user.get("id") or user.get("_id"))
    await repo.save_media(user_id, ad_account_id, {
        "type": "image",
        "result": result,
    })
    return result


@router.get("/media/images/{ad_account_id}", summary="List images", tags=["meta-ads-media"])
async def list_images(
    ad_account_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    return await meta_svc.list_images(token, ad_account_id)


@router.post("/media/upload-video", summary="Upload a video from URL", tags=["meta-ads-media"])
async def upload_video(
    body: VideoUploadInput,
    token: Annotated[str, Depends(require_meta_connection)],
    user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[MetaAdsRepository, Depends(get_meta_repo)],
):
    result = await meta_svc.upload_video(token, body.ad_account_id, body.video_url, body.title)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    user_id = str(user.get("id") or user.get("_id"))
    await repo.save_media(user_id, body.ad_account_id, {
        "type": "video",
        "video_url": body.video_url,
        "title": body.title,
        "result": result,
    })
    return result


@router.get("/media/videos/{ad_account_id}", summary="List videos", tags=["meta-ads-media"])
async def list_videos(
    ad_account_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    return await meta_svc.list_videos(token, ad_account_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Ad Creatives
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/creatives/{ad_account_id}", summary="List creatives", tags=["meta-ads-creatives"])
async def list_creatives(
    ad_account_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    return await meta_svc.list_creatives(token, ad_account_id)


@router.get("/creatives/get/{creative_id}", summary="Get a single creative", tags=["meta-ads-creatives"])
async def get_creative(
    creative_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    return await meta_svc.get_creative(token, creative_id)


@router.post("/creatives/link", summary="Create an image/link creative", tags=["meta-ads-creatives"])
async def create_link_creative(
    body: LinkCreativeInput,
    token: Annotated[str, Depends(require_meta_connection)],
    user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[MetaAdsRepository, Depends(get_meta_repo)],
):
    result = await meta_svc.create_link_creative(
        token, body.ad_account_id, body.page_id, body.name,
        body.image_hash, body.link, body.message, body.headline,
        body.description, body.call_to_action_type, body.instagram_actor_id,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    user_id = str(user.get("id") or user.get("_id"))
    db_id = await repo.save_creative(user_id, body.ad_account_id, {
        "type": "link",
        "meta_id": result.get("id"),
        "name": body.name,
        "page_id": body.page_id,
        "image_hash": body.image_hash,
        "link": body.link,
    })
    return {"status": "created", "meta_id": result.get("id"), "db_id": db_id}


@router.post("/creatives/video", summary="Create a video creative", tags=["meta-ads-creatives"])
async def create_video_creative(
    body: VideoCreativeInput,
    token: Annotated[str, Depends(require_meta_connection)],
    user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[MetaAdsRepository, Depends(get_meta_repo)],
):
    result = await meta_svc.create_video_creative(
        token, body.ad_account_id, body.page_id, body.name,
        body.video_id, body.title, body.message, body.description,
        body.call_to_action_type, body.link, body.instagram_actor_id,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    user_id = str(user.get("id") or user.get("_id"))
    db_id = await repo.save_creative(user_id, body.ad_account_id, {
        "type": "video",
        "meta_id": result.get("id"),
        "name": body.name,
        "page_id": body.page_id,
        "video_id": body.video_id,
        "link": body.link,
    })
    return {"status": "created", "meta_id": result.get("id"), "db_id": db_id}


# ═══════════════════════════════════════════════════════════════════════════════
# Ads
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/ads/{ad_account_id}", summary="List ads", tags=["meta-ads-ads"])
async def list_ads(
    ad_account_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
    status_filter: str | None = None,
):
    return await meta_svc.list_ads(token, ad_account_id, status_filter)


@router.get("/ads/get/{ad_id}", summary="Get a single ad", tags=["meta-ads-ads"])
async def get_ad(
    ad_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    return await meta_svc.get_ad(token, ad_id)


@router.post("/ads", summary="Create an ad", tags=["meta-ads-ads"])
async def create_ad(
    body: AdCreate,
    token: Annotated[str, Depends(require_meta_connection)],
    user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[MetaAdsRepository, Depends(get_meta_repo)],
):
    payload: dict = {
        "name": body.name,
        "adset_id": body.adset_id,
        "creative": {"creative_id": body.creative_id},
        "status": body.status,
    }
    if body.tracking_specs:
        payload["tracking_specs"] = body.tracking_specs

    result = await meta_svc.create_ad(token, body.ad_account_id, payload)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    user_id = str(user.get("id") or user.get("_id"))
    db_id = await repo.save_ad(user_id, body.ad_account_id, {
        "meta_id": result.get("id"),
        "name": body.name,
        "adset_id": body.adset_id,
        "creative_id": body.creative_id,
        "status": body.status,
    })
    return {"status": "created", "meta_id": result.get("id"), "db_id": db_id}


@router.patch("/ads/{ad_id}", summary="Update an ad", tags=["meta-ads-ads"])
async def update_ad(
    ad_id: str,
    body: AdUpdate,
    token: Annotated[str, Depends(require_meta_connection)],
):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await meta_svc.update_ad(token, ad_id, fields)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.delete("/ads/{ad_id}", summary="Delete an ad", tags=["meta-ads-ads"])
async def delete_ad(
    ad_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    result = await meta_svc.delete_ad(token, ad_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Insights / Analytics
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/insights", summary="Get metrics for campaign/adset/ad", tags=["meta-ads-insights"])
async def insights(
    body: InsightsInput,
    token: Annotated[str, Depends(require_meta_connection)],
    user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[MetaAdsRepository, Depends(get_meta_repo)],
):
    result = await meta_svc.get_insights(
        token, body.object_id, body.level, body.fields, body.date_preset,
        body.time_increment, body.breakdowns, body.action_attribution_windows,
        body.time_range_since, body.time_range_until,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    user_id = str(user.get("id") or user.get("_id"))
    await repo.save_insights(user_id, body.object_id, {
        "level": body.level,
        "data": result.get("data", []),
    })
    return result


@router.post("/insights/account", summary="Get account-level metrics", tags=["meta-ads-insights"])
async def account_insights(
    body: AccountInsightsInput,
    token: Annotated[str, Depends(require_meta_connection)],
    user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[MetaAdsRepository, Depends(get_meta_repo)],
):
    result = await meta_svc.get_account_insights(
        token, body.ad_account_id, body.fields, body.date_preset,
        body.time_increment, body.breakdowns,
        body.time_range_since, body.time_range_until,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    user_id = str(user.get("id") or user.get("_id"))
    await repo.save_insights(user_id, f"act_{body.ad_account_id}", {
        "level": "account",
        "data": result.get("data", []),
    })
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Custom Audiences
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/audiences/{ad_account_id}", summary="List custom audiences", tags=["meta-ads-audiences"])
async def list_audiences(
    ad_account_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    return await meta_svc.list_audiences(token, ad_account_id)


@router.post("/audiences", summary="Create a custom audience", tags=["meta-ads-audiences"])
async def create_audience(
    body: AudienceCreate,
    token: Annotated[str, Depends(require_meta_connection)],
    user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[MetaAdsRepository, Depends(get_meta_repo)],
):
    result = await meta_svc.create_custom_audience(
        token, body.ad_account_id, body.name, body.subtype, body.description,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    user_id = str(user.get("id") or user.get("_id"))
    db_id = await repo.save_audience(user_id, body.ad_account_id, {
        "meta_id": result.get("id"),
        "name": body.name,
        "subtype": body.subtype,
        "description": body.description,
    })
    return {"status": "created", "meta_id": result.get("id"), "db_id": db_id}


@router.delete("/audiences/{audience_id}", summary="Delete a custom audience", tags=["meta-ads-audiences"])
async def delete_audience(
    audience_id: str,
    token: Annotated[str, Depends(require_meta_connection)],
):
    result = await meta_svc.delete_audience(token, audience_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Lead Generation
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/leads/form", summary="Create a lead gen form on a Facebook Page", tags=["meta-ads-leads"])
async def create_lead_form(
    body: LeadFormCreate,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    repo: Annotated[MetaAdsRepository, Depends(get_meta_repo)],
):
    page_token = await get_page_token(body.page_id, user, db)
    questions = [q.model_dump(exclude_none=True) for q in body.questions]
    result = await meta_svc.create_lead_form(
        page_token, body.page_id, body.name, questions,
        body.privacy_policy_url, body.thank_you_message,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    user_id = str(user.get("id") or user.get("_id"))
    db_id = await repo.save_lead_form(user_id, body.page_id, {
        "meta_id": result.get("id"),
        "name": body.name,
        "questions": questions,
    })
    return {"status": "created", "meta_id": result.get("id"), "db_id": db_id}


@router.get("/leads/forms/{page_id}", summary="List lead gen forms for a page", tags=["meta-ads-leads"])
async def list_lead_forms(
    page_id: str,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
):
    page_token = await get_page_token(page_id, user, db)
    return await meta_svc.get_lead_forms(page_token, page_id)


@router.get("/leads/responses/{form_id}", summary="Get submitted leads from a form", tags=["meta-ads-leads"])
async def get_lead_responses(
    form_id: str,
    page_id: str = Query(..., description="Page ID that owns this form (needed for Page Access Token)"),
    user: Annotated[dict, Depends(get_current_user)] = None,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)] = None,
    repo: Annotated[MetaAdsRepository, Depends(get_meta_repo)] = None,
):
    page_token = await get_page_token(page_id, user, db)
    result = await meta_svc.get_leads(page_token, form_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    leads_data = result.get("data", [])
    if leads_data:
        user_id = str(user.get("id") or user.get("_id"))
        await repo.save_leads(user_id, form_id, leads_data)

    return result
