"""Pydantic schemas for Google Ads API requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, field_validator


# ─── Request Schemas ──────────────────────────────────────────────────────────

class BudgetCreateRequest(BaseModel):
    name: str
    amount_inr: int
    delivery_method: str = "STANDARD"   # STANDARD | ACCELERATED

    @field_validator("delivery_method")
    @classmethod
    def validate_delivery_method(cls, v: str) -> str:
        allowed = {"STANDARD", "ACCELERATED"}
        if v.upper() not in allowed:
            raise ValueError(f"delivery_method must be one of {allowed}")
        return v.upper()


class CampaignCreateRequest(BaseModel):
    name: str
    budget_resource: str
    channel_type: str = "SEARCH"
    status: str = "PAUSED"

    @field_validator("channel_type")
    @classmethod
    def validate_channel(cls, v: str) -> str:
        allowed = {"SEARCH", "DISPLAY", "VIDEO", "SHOPPING", "HOTEL", "LOCAL", "SMART", "MULTI_CHANNEL"}
        if v.upper() not in allowed:
            raise ValueError(f"channel_type must be one of {allowed}")
        return v.upper()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"ENABLED", "PAUSED"}
        if v.upper() not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v.upper()


class CampaignStatusUpdateRequest(BaseModel):
    status: str  # ENABLED | PAUSED

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"ENABLED", "PAUSED"}
        if v.upper() not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v.upper()


class AdGroupCreateRequest(BaseModel):
    name: str
    campaign_resource: str
    cpc_bid_inr: int
    type_: str = "SEARCH_STANDARD"
    status: str = "ENABLED"

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"ENABLED", "PAUSED", "REMOVED"}
        if v.upper() not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v.upper()


class AdCreateRequest(BaseModel):
    ad_group_resource: str
    final_url: str
    headlines: List[str]
    descriptions: List[str]
    status: str = "ENABLED"

    @field_validator("headlines")
    @classmethod
    def validate_headlines(cls, v: List[str]) -> List[str]:
        if len(v) < 3:
            raise ValueError("Minimum 3 headlines required")
        for h in v:
            if len(h) > 30:
                raise ValueError(f"Headline too long (max 30 chars): '{h}'")
            if len(h) < 3:
                raise ValueError(f"Headline too short (min 3 chars): '{h}'")
        return v

    @field_validator("descriptions")
    @classmethod
    def validate_descriptions(cls, v: List[str]) -> List[str]:
        if len(v) < 2:
            raise ValueError("Minimum 2 descriptions required")
        for d in v:
            if len(d) > 90:
                raise ValueError(f"Description too long (max 90 chars): '{d}'")
            if len(d) < 10:
                raise ValueError(f"Description too short (min 10 chars): '{d}'")
        return v


class KeywordsAddRequest(BaseModel):
    ad_group_resource: str
    keywords: List[str]
    match_type: str = "BROAD"

    @field_validator("match_type")
    @classmethod
    def validate_match_type(cls, v: str) -> str:
        allowed = {"BROAD", "PHRASE", "EXACT"}
        if v.upper() not in allowed:
            raise ValueError(f"match_type must be one of {allowed}")
        return v.upper()

    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("keywords list cannot be empty")
        return v


# ─── Response Schemas ─────────────────────────────────────────────────────────

class BudgetResponse(BaseModel):
    status: str
    budget_resource: str
    db_id: str


class CampaignResponse(BaseModel):
    status: str
    campaign_resource: str
    db_id: str


class AdGroupResponse(BaseModel):
    status: str
    ad_group_resource: str
    db_id: str


class AdResponse(BaseModel):
    status: str
    ad_resource: str
    db_id: str


class KeywordsResponse(BaseModel):
    status: str
    keywords_added: List[str]
    db_id: str


class CampaignItem(BaseModel):
    id: int
    name: str
    status: str
    resource: str


class CampaignsListResponse(BaseModel):
    campaigns: List[CampaignItem]
    count: int


class AccountsResponse(BaseModel):
    accounts: List[str]


# ─── Metrics Schemas ──────────────────────────────────────────────────────────

class CampaignMetric(BaseModel):
    campaign_id: int
    campaign_name: str
    campaign_status: str
    date: Optional[str] = None
    clicks: int
    impressions: int
    cost_inr: float        # cost in INR (converted from micros)
    conversions: float
    ctr: float             # click-through rate (0.0–1.0)


class MetricsResponse(BaseModel):
    metrics: List[CampaignMetric]
    count: int


# ─── Dashboard Schemas ────────────────────────────────────────────────────────

# ─── Connection Schemas ───────────────────────────────────────────────────────

class OAuthUrlResponse(BaseModel):
    url: str


class ConnectionStatus(BaseModel):
    connected: bool
    connected_at: Optional[str] = None


# ─── Dashboard Schemas ────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_clicks: int
    total_impressions: int
    total_cost_inr: float
    total_conversions: float
    avg_ctr: float
    campaign_count: int
    active_campaigns: int
    paused_campaigns: int


# ─── AI Insights Schemas ──────────────────────────────────────────────────────

class AiInsight(BaseModel):
    campaign_id: int
    campaign_name: str
    insight_type: str    # LOW_CTR | HIGH_SPEND_LOW_CONV | ZERO_CONVERSIONS | GOOD_PERFORMANCE
    severity: str        # INFO | WARNING | CRITICAL
    message: str
    recommendation: str


class InsightsResponse(BaseModel):
    insights: List[AiInsight]
    count: int
    generated_at: str
