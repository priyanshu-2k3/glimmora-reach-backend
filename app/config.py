"""Application configuration from environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    secret_key: str = "change-me-in-production-min-32-characters"

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "glimmora_reach"

    # JWT
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 15
    jwt_refresh_expire_days: int = 7

    # OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/oauth/google/callback"
    # Where to send user after OAuth (SPA URL; tokens will be in fragment)
    frontend_oauth_redirect_uri: str = "http://localhost:3000/oauth/callback"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Google Ads API
    google_ads_developer_token: str = ""
    google_ads_redirect_uri: str = "http://localhost:8000/api/v1/google-ads/oauth/callback"

    # Super Admin seed (for seed.py)
    super_admin_email: str = ""
    super_admin_password: str = ""

    # Invite email (optional)
    invite_base_url: str = "http://localhost:3000"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@glimmora.io"

    @property
    def cors_origins_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        # Always include the production frontend
        production = "https://glimmora-reach-frontend.vercel.app"
        if production not in origins:
            origins.append(production)
        return origins

    @property
    def jwt_secret(self) -> str:
        return self.secret_key


settings = Settings()
