"""Google Ads OAuth helpers — generate auth URL, exchange code for tokens."""

import urllib.parse

import httpx
from app.services.google_ads_config import load_google_ads_base_config


def _load_yaml_creds() -> dict:
    return load_google_ads_base_config()


def get_oauth_url(state: str, redirect_uri: str) -> str:
    """Build the Google OAuth2 authorization URL for the Ads scope."""
    creds = _load_yaml_creds()
    params = {
        "client_id": creds["client_id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/adwords",
        "access_type": "offline",
        "prompt": "consent",   # always return refresh_token
        "state": state,
    }
    return "https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params)


async def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict:
    """Exchange an authorization code for access + refresh tokens."""
    creds = _load_yaml_creds()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": creds["client_id"],
                "client_secret": creds["client_secret"],
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
    resp.raise_for_status()
    return resp.json()
