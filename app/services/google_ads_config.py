"""Google Ads SDK configuration loader.

Loads credentials from `google-ads.yaml` when present, otherwise falls back to
environment-backed app settings.
"""

from pathlib import Path

import yaml

from app.config import settings


def load_google_ads_base_config() -> dict:
    """Return base Google Ads config without per-user refresh token."""
    yaml_path = Path("google-ads.yaml")
    if yaml_path.exists():
        with yaml_path.open("r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f) or {}
        if loaded.get("developer_token") and loaded.get("client_id") and loaded.get("client_secret"):
            return loaded

    # Fallback to env settings.
    if not settings.google_ads_developer_token:
        raise ValueError("Missing Google Ads developer token.")
    if not settings.google_client_id or not settings.google_client_secret:
        raise ValueError("Missing Google OAuth client_id/client_secret for Google Ads.")

    return {
        "developer_token": settings.google_ads_developer_token,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "use_proto_plus": True,
    }
