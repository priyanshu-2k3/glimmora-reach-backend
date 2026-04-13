"""Meta (Facebook) Graph API service layer — all external API calls."""

from typing import Any

import httpx
from fastapi import UploadFile

from app.config import settings

GRAPH_VERSION = settings.meta_graph_version
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"

APP_ID = settings.meta_app_id
APP_SECRET = settings.meta_app_secret
REDIRECT_URI = settings.meta_redirect_uri


def _h(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# -- Auth --------------------------------------------------------------------

def build_oauth_url(state: str | None = None) -> str:
    """Return the Facebook OAuth dialog URL."""
    url = (
        f"https://www.facebook.com/{GRAPH_VERSION}/dialog/oauth?"
        f"client_id={APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=ads_management,ads_read,business_management,"
        f"leads_retrieval,pages_manage_ads,pages_read_engagement"
        f"&response_type=code"
    )
    if state:
        url += f"&state={state}"
    return url


async def exchange_code_for_token(code: str) -> dict:
    """Exchange the temporary OAuth code for a short-lived access token."""
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "client_secret": APP_SECRET,
        "code": code,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GRAPH_URL}/oauth/access_token", params=params)
        return resp.json()


async def exchange_long_lived_token(short_token: str) -> dict:
    """Exchange a short-lived token for a long-lived token (~60 days)."""
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": short_token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GRAPH_URL}/oauth/access_token", params=params)
        return resp.json()


# -- Account -----------------------------------------------------------------

async def get_ad_accounts(token: str) -> dict:
    params = {
        "fields": "id,name,currency,timezone_name,account_status,business",
        "access_token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GRAPH_URL}/me/adaccounts", params=params)
        return resp.json()


async def get_account_details(token: str, ad_account_id: str) -> dict:
    params = {
        "fields": "id,name,currency,timezone_name,account_status,spend_cap,amount_spent,balance,business",
        "access_token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GRAPH_URL}/act_{ad_account_id}", params=params)
        return resp.json()


async def get_pages(token: str) -> dict:
    params = {
        "fields": "id,name,category,access_token,tasks",
        "access_token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GRAPH_URL}/me/accounts", params=params)
        return resp.json()


# -- Campaigns ---------------------------------------------------------------

async def list_campaigns(token: str, ad_account_id: str,
                         status_filter: str | None = None) -> dict:
    params = {
        "fields": "id,name,objective,status,created_time,start_time,stop_time,"
                  "daily_budget,lifetime_budget,budget_remaining,"
                  "is_adset_budget_sharing_enabled,special_ad_categories",
        "access_token": token,
    }
    if status_filter:
        params["effective_status"] = f'["{status_filter}"]'
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GRAPH_URL}/act_{ad_account_id}/campaigns", params=params,
        )
        return resp.json()


async def get_campaign(token: str, campaign_id: str) -> dict:
    params = {
        "fields": "id,name,objective,status,created_time,start_time,stop_time,"
                  "daily_budget,lifetime_budget,budget_remaining,"
                  "is_adset_budget_sharing_enabled,special_ad_categories",
        "access_token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GRAPH_URL}/{campaign_id}", params=params)
        return resp.json()


async def create_campaign(token: str, ad_account_id: str,
                          payload: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/act_{ad_account_id}/campaigns",
            json=payload, headers=_h(token),
        )
        return resp.json()


async def update_campaign(token: str, campaign_id: str,
                          fields: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/{campaign_id}", json=fields, headers=_h(token),
        )
        return resp.json()


async def delete_campaign(token: str, campaign_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{GRAPH_URL}/{campaign_id}", headers=_h(token),
        )
        return resp.json()


# -- Ad Sets -----------------------------------------------------------------

async def list_adsets(token: str, ad_account_id: str,
                      status_filter: str | None = None) -> dict:
    params = {
        "fields": "id,name,status,campaign_id,daily_budget,lifetime_budget,"
                  "optimization_goal,billing_event,bid_strategy,bid_amount,"
                  "targeting,start_time,end_time,promoted_object,created_time",
        "access_token": token,
    }
    if status_filter:
        params["effective_status"] = f'["{status_filter}"]'
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GRAPH_URL}/act_{ad_account_id}/adsets", params=params,
        )
        return resp.json()


async def get_adset(token: str, adset_id: str) -> dict:
    params = {
        "fields": "id,name,status,campaign_id,daily_budget,lifetime_budget,"
                  "optimization_goal,billing_event,bid_strategy,targeting,"
                  "start_time,end_time,promoted_object,created_time",
        "access_token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GRAPH_URL}/{adset_id}", params=params)
        return resp.json()


async def create_adset(token: str, ad_account_id: str,
                       payload: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/act_{ad_account_id}/adsets",
            json=payload, headers=_h(token),
        )
        return resp.json()


async def update_adset(token: str, adset_id: str, fields: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/{adset_id}", json=fields, headers=_h(token),
        )
        return resp.json()


async def delete_adset(token: str, adset_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{GRAPH_URL}/{adset_id}", headers=_h(token),
        )
        return resp.json()


# -- Ad Creatives ------------------------------------------------------------

async def list_creatives(token: str, ad_account_id: str) -> dict:
    params = {
        "fields": "id,name,object_story_spec,asset_feed_spec,status,thumbnail_url",
        "access_token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GRAPH_URL}/act_{ad_account_id}/adcreatives", params=params,
        )
        return resp.json()


async def get_creative(token: str, creative_id: str) -> dict:
    params = {
        "fields": "id,name,object_story_spec,asset_feed_spec,status,thumbnail_url",
        "access_token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GRAPH_URL}/{creative_id}", params=params)
        return resp.json()


async def create_link_creative(token: str, ad_account_id: str,
                                page_id: str, name: str,
                                image_hash: str, link: str,
                                message: str, headline: str,
                                description: str,
                                call_to_action_type: str,
                                instagram_actor_id: str | None = None) -> dict:
    link_data: dict[str, Any] = {
        "image_hash": image_hash,
        "link": link,
        "message": message,
        "name": headline,
        "description": description,
        "call_to_action": {"type": call_to_action_type, "value": {"link": link}},
    }
    story_spec: dict[str, Any] = {"page_id": page_id, "link_data": link_data}
    if instagram_actor_id:
        story_spec["instagram_actor_id"] = instagram_actor_id
    payload = {"name": name, "object_story_spec": story_spec}
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/act_{ad_account_id}/adcreatives",
            json=payload, headers=_h(token),
        )
        return resp.json()


async def create_video_creative(token: str, ad_account_id: str,
                                 page_id: str, name: str,
                                 video_id: str, title: str,
                                 message: str, description: str,
                                 call_to_action_type: str, link: str,
                                 instagram_actor_id: str | None = None) -> dict:
    video_data: dict[str, Any] = {
        "video_id": video_id,
        "title": title,
        "message": message,
        "description": description,
        "call_to_action": {"type": call_to_action_type, "value": {"link": link}},
    }
    story_spec: dict[str, Any] = {"page_id": page_id, "video_data": video_data}
    if instagram_actor_id:
        story_spec["instagram_actor_id"] = instagram_actor_id
    payload = {"name": name, "object_story_spec": story_spec}
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/act_{ad_account_id}/adcreatives",
            json=payload, headers=_h(token),
        )
        return resp.json()


# -- Media (Images & Videos) -------------------------------------------------

async def upload_image(token: str, ad_account_id: str,
                       image: UploadFile) -> dict:
    content = await image.read()
    files = {"filename": (image.filename, content, image.content_type)}
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/act_{ad_account_id}/adimages",
            files=files, headers=_h(token),
        )
        return resp.json()


async def list_images(token: str, ad_account_id: str) -> dict:
    params = {
        "fields": "hash,name,url,url_128,width,height,created_time",
        "access_token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GRAPH_URL}/act_{ad_account_id}/adimages", params=params,
        )
        return resp.json()


async def upload_video(token: str, ad_account_id: str,
                       video_url: str, title: str = "Ad Video") -> dict:
    payload = {"file_url": video_url, "title": title}
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{GRAPH_URL}/act_{ad_account_id}/advideos",
            json=payload, headers=_h(token),
        )
        return resp.json()


async def list_videos(token: str, ad_account_id: str) -> dict:
    params = {
        "fields": "id,title,status,created_time,picture,length",
        "access_token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GRAPH_URL}/act_{ad_account_id}/advideos", params=params,
        )
        return resp.json()


# -- Ads ---------------------------------------------------------------------

async def list_ads(token: str, ad_account_id: str,
                   status_filter: str | None = None) -> dict:
    params = {
        "fields": "id,name,status,adset_id,creative{id,name,thumbnail_url},"
                  "created_time,effective_status",
        "access_token": token,
    }
    if status_filter:
        params["effective_status"] = f'["{status_filter}"]'
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GRAPH_URL}/act_{ad_account_id}/ads", params=params,
        )
        return resp.json()


async def get_ad(token: str, ad_id: str) -> dict:
    params = {
        "fields": "id,name,status,adset_id,creative{id,name,thumbnail_url},"
                  "created_time,effective_status",
        "access_token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GRAPH_URL}/{ad_id}", params=params)
        return resp.json()


async def create_ad(token: str, ad_account_id: str,
                    payload: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/act_{ad_account_id}/ads",
            json=payload, headers=_h(token),
        )
        return resp.json()


async def update_ad(token: str, ad_id: str, fields: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/{ad_id}", json=fields, headers=_h(token),
        )
        return resp.json()


async def delete_ad(token: str, ad_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{GRAPH_URL}/{ad_id}", headers=_h(token),
        )
        return resp.json()


# -- Insights / Analytics ---------------------------------------------------

async def get_insights(token: str, object_id: str, level: str,
                       fields: str, date_preset: str,
                       time_increment: str,
                       breakdowns: str | None = None,
                       action_attribution_windows: str | None = None,
                       time_range_since: str | None = None,
                       time_range_until: str | None = None) -> dict:
    params: dict[str, str] = {
        "level": level,
        "fields": fields,
        "time_increment": time_increment,
        "access_token": token,
    }
    if breakdowns:
        params["breakdowns"] = breakdowns
    if action_attribution_windows:
        params["action_attribution_windows"] = action_attribution_windows
    if time_range_since and time_range_until:
        params["time_range"] = (
            f'{{"since":"{time_range_since}","until":"{time_range_until}"}}'
        )
    else:
        params["date_preset"] = date_preset
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GRAPH_URL}/{object_id}/insights", params=params,
        )
        return resp.json()


async def get_account_insights(token: str, ad_account_id: str,
                                fields: str, date_preset: str,
                                time_increment: str,
                                breakdowns: str | None = None,
                                time_range_since: str | None = None,
                                time_range_until: str | None = None) -> dict:
    params: dict[str, str] = {
        "level": "account",
        "fields": fields,
        "time_increment": time_increment,
        "access_token": token,
    }
    if breakdowns:
        params["breakdowns"] = breakdowns
    if time_range_since and time_range_until:
        params["time_range"] = (
            f'{{"since":"{time_range_since}","until":"{time_range_until}"}}'
        )
    else:
        params["date_preset"] = date_preset
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GRAPH_URL}/act_{ad_account_id}/insights", params=params,
        )
        return resp.json()


# -- Custom Audiences --------------------------------------------------------

async def list_audiences(token: str, ad_account_id: str) -> dict:
    params = {
        "fields": "id,name,subtype,approximate_count,created_time,description",
        "access_token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GRAPH_URL}/act_{ad_account_id}/customaudiences", params=params,
        )
        return resp.json()


async def create_custom_audience(token: str, ad_account_id: str,
                                  name: str, subtype: str,
                                  description: str) -> dict:
    payload = {"name": name, "subtype": subtype, "description": description}
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/act_{ad_account_id}/customaudiences",
            json=payload, headers=_h(token),
        )
        return resp.json()


async def delete_audience(token: str, audience_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{GRAPH_URL}/{audience_id}", headers=_h(token),
        )
        return resp.json()


# -- Lead Gen ----------------------------------------------------------------

async def create_lead_form(token: str, page_id: str, name: str,
                           questions: list[dict],
                           privacy_policy_url: str,
                           thank_you_message: str) -> dict:
    payload = {
        "name": name,
        "questions": questions,
        "privacy_policy": {"url": privacy_policy_url},
        "thank_you_page": {
            "title": "Thank You",
            "body": thank_you_message,
            "button_type": "NONE",
        },
        "access_token": token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/{page_id}/leadgen_forms",
            json=payload, headers=_h(token),
        )
        return resp.json()


async def get_lead_forms(token: str, page_id: str) -> dict:
    params = {
        "access_token": token,
        "fields": "id,name,status,leads_count,created_time",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GRAPH_URL}/{page_id}/leadgen_forms", params=params,
        )
        return resp.json()


async def get_leads(token: str, form_id: str) -> dict:
    params = {
        "access_token": token,
        "fields": "id,created_time,field_data",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GRAPH_URL}/{form_id}/leads", params=params,
        )
        return resp.json()
