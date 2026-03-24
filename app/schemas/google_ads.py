"""Pydantic schemas for Google Ads API requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl, field_validator


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
    budget_resource: str                 # e.g. customers/XXX/campaignBudgets/YYY
    channel_type: str = "SEARCH"         # SEARCH | DISPLAY | VIDEO | SHOPPING
    status: str = "PAUSED"              # ENABLED | PAUSED

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


class AdGroupCreateRequest(BaseModel):
    name: str
    campaign_resource: str               # e.g. customers/XXX/campaigns/YYY
    cpc_bid_inr: int
    type_: str = "SEARCH_STANDARD"
    status: str = "ENABLED"             # ENABLED | PAUSED | REMOVED

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"ENABLED", "PAUSED", "REMOVED"}
        if v.upper() not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v.upper()


class AdCreateRequest(BaseModel):
    ad_group_resource: str               # e.g. customers/XXX/adGroups/YYY
    final_url: str
    headlines: List[str]                 # min 3, max 30 chars each
    descriptions: List[str]             # min 2, max 90 chars each
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
    ad_group_resource: str               # e.g. customers/XXX/adGroups/YYY
    keywords: List[str]
    match_type: str = "BROAD"           # BROAD | PHRASE | EXACT

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
