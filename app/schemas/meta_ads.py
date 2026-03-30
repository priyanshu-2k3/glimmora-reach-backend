"""Pydantic request/response schemas for Meta (Facebook) Ads."""

from typing import Any, Optional

from pydantic import BaseModel, Field


# -- OAuth / Connection -------------------------------------------------------

class OAuthUrlResponse(BaseModel):
    url: str

class ConnectionStatus(BaseModel):
    connected: bool
    connected_at: str | None = None


# -- Campaigns ----------------------------------------------------------------

class CampaignCreate(BaseModel):
    ad_account_id: str
    name: str
    objective: str = Field("OUTCOME_TRAFFIC", description="OUTCOME_TRAFFIC|OUTCOME_LEADS|OUTCOME_SALES|OUTCOME_ENGAGEMENT|OUTCOME_APP_PROMOTION|OUTCOME_AWARENESS")
    status: str = Field("PAUSED", description="ACTIVE|PAUSED")
    special_ad_categories: list[str] = Field(default_factory=list, description='[]|["CREDIT"]|["EMPLOYMENT"]|["HOUSING"]')
    is_adset_budget_sharing_enabled: bool = False
    daily_budget: str | None = Field(None, description="In cents, e.g. '5000' = $50")
    lifetime_budget: str | None = None
    start_time: str | None = Field(None, description="ISO 8601, e.g. 2024-04-01T00:00:00+0000")
    stop_time: str | None = None
    bid_strategy: str | None = Field(None, description="LOWEST_COST_WITHOUT_CAP|LOWEST_COST_WITH_BID_CAP|COST_CAP|LOWEST_COST_WITH_MIN_ROAS")

class CampaignUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    daily_budget: str | None = None
    lifetime_budget: str | None = None
    start_time: str | None = None
    stop_time: str | None = None
    bid_strategy: str | None = None
    special_ad_categories: list[str] | None = None


# -- Ad Sets ------------------------------------------------------------------

class AdSetCreate(BaseModel):
    ad_account_id: str
    campaign_id: str
    name: str
    status: str = "PAUSED"
    daily_budget: str | None = "1000"
    lifetime_budget: str | None = None
    billing_event: str = Field("IMPRESSIONS", description="IMPRESSIONS|LINK_CLICKS|APP_INSTALLS|NONE")
    optimization_goal: str = Field("LINK_CLICKS", description="LINK_CLICKS|IMPRESSIONS|REACH|LEAD_GENERATION|OFFSITE_CONVERSIONS|APP_INSTALLS|ENGAGED_USERS|PAGE_LIKES|EVENT_RESPONSES|VALUE")
    bid_strategy: str | None = Field(None, description="LOWEST_COST_WITHOUT_CAP|LOWEST_COST_WITH_BID_CAP|COST_CAP")
    bid_amount: str | None = Field(None, description="Required for BID_CAP strategy, in cents")
    countries: list[str] = Field(default_factory=lambda: ["US"])
    age_min: int = 18
    age_max: int = 65
    genders: list[int] | None = Field(None, description="1=Male, 2=Female, omit for all")
    publisher_platforms: list[str] | None = Field(None, description="facebook|instagram|audience_network|messenger")
    facebook_positions: list[str] | None = None
    instagram_positions: list[str] | None = None
    device_platforms: list[str] | None = Field(None, description="mobile|desktop")
    interests: list[str] | None = Field(None, description="Interest IDs from Meta Targeting API")
    behaviors: list[str] | None = None
    custom_audiences: list[str] | None = None
    excluded_audiences: list[str] | None = None
    promoted_object: dict[str, Any] | None = None
    start_time: str | None = None
    end_time: str | None = None

class AdSetUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    daily_budget: str | None = None
    lifetime_budget: str | None = None
    bid_amount: str | None = None
    start_time: str | None = None
    end_time: str | None = None


# -- Media --------------------------------------------------------------------

class VideoUploadInput(BaseModel):
    ad_account_id: str
    video_url: str = Field(..., description="Publicly accessible URL of the video")
    title: str = "Ad Video"


# -- Ad Creatives -------------------------------------------------------------

class LinkCreativeInput(BaseModel):
    ad_account_id: str
    page_id: str
    name: str = "Link Creative"
    image_hash: str
    link: str
    message: str = "Check this out"
    headline: str = "Limited Offer"
    description: str = ""
    call_to_action_type: str = Field("LEARN_MORE", description="LEARN_MORE|SHOP_NOW|SIGN_UP|DOWNLOAD|CONTACT_US|BOOK_TRAVEL|GET_OFFER|GET_QUOTE|SUBSCRIBE|APPLY_NOW|DONATE|WATCH_MORE")
    instagram_actor_id: str | None = None

class VideoCreativeInput(BaseModel):
    ad_account_id: str
    page_id: str
    name: str = "Video Creative"
    video_id: str
    title: str = "Watch Now"
    message: str = "Check this out"
    description: str = ""
    call_to_action_type: str = "LEARN_MORE"
    link: str
    instagram_actor_id: str | None = None


# -- Ads ----------------------------------------------------------------------

class AdCreate(BaseModel):
    ad_account_id: str
    adset_id: str
    creative_id: str
    name: str = "New Ad"
    status: str = "PAUSED"
    tracking_specs: list[dict[str, Any]] | None = None

class AdUpdate(BaseModel):
    name: str | None = None
    status: str | None = None


# -- Insights / Analytics ----------------------------------------------------

class InsightsInput(BaseModel):
    object_id: str = Field(..., description="campaign_id, adset_id, ad_id, or act_ACCOUNT_ID")
    level: str = Field("campaign", description="account|campaign|adset|ad")
    fields: str = "impressions,clicks,spend,reach,ctr,cpc,cpm,frequency,unique_clicks,cost_per_unique_click,actions,action_values,cost_per_action_type,video_p25_watched_actions,video_p50_watched_actions,video_p75_watched_actions,video_p100_watched_actions"
    date_preset: str = Field("last_30d", description="today|yesterday|last_3d|last_7d|last_14d|last_28d|last_30d|last_90d|this_month|last_month|this_quarter|lifetime")
    time_increment: str = Field("1", description="1=daily|7=weekly|monthly|all_days")
    breakdowns: str | None = None
    action_attribution_windows: str | None = None
    time_range_since: str | None = Field(None, description="Overrides date_preset, e.g. 2024-01-01")
    time_range_until: str | None = None

class AccountInsightsInput(BaseModel):
    ad_account_id: str
    fields: str = "impressions,clicks,spend,reach,ctr,cpc,cpm,actions,action_values"
    date_preset: str = "last_30d"
    time_increment: str = "all_days"
    breakdowns: str | None = None
    time_range_since: str | None = None
    time_range_until: str | None = None


# -- Custom Audiences ---------------------------------------------------------

class AudienceCreate(BaseModel):
    ad_account_id: str
    name: str
    subtype: str = Field("CUSTOM", description="CUSTOM|WEBSITE|APP|OFFLINE_CONVERSION|CLAIM|PARTNER|MANAGED|VIDEO|LOOKALIKE|ENGAGEMENT|BAG_OF_ACCOUNTS")
    description: str = ""


# -- Lead Gen -----------------------------------------------------------------

class LeadFormQuestion(BaseModel):
    type: str = Field(..., description="FULL_NAME|FIRST_NAME|LAST_NAME|EMAIL|PHONE|CITY|STATE|COUNTRY|ZIP|COMPANY_NAME|JOB_TITLE|WORK_EMAIL|WEBSITE|CUSTOM")
    label: str | None = Field(None, description="Required for CUSTOM type")
    key: str | None = Field(None, description="Required for CUSTOM type")

class LeadFormCreate(BaseModel):
    page_id: str
    name: str
    questions: list[LeadFormQuestion] = Field(
        default_factory=lambda: [
            LeadFormQuestion(type="FULL_NAME"),
            LeadFormQuestion(type="EMAIL"),
            LeadFormQuestion(type="PHONE"),
        ]
    )
    privacy_policy_url: str
    thank_you_message: str = "Thank you! We will be in touch soon."
