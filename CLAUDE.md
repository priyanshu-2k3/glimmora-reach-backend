# CLAUDE.md — Developer Instructions for Claude Code

## MANDATORY: After Every New Feature

Whenever you create or modify a route, schema, or API feature, you MUST update `TESTING.md`:

1. Add the new route(s) to the relevant table section
2. Fill in: Route, Method, Headers, Request Params, Response, What It Does
3. If the new route has dependencies (e.g. must run after another API), add it to the Testing Order section in the correct position
4. If new query params, path params, or body fields are introduced, add examples to the Quick Reference table if they are non-obvious

Do not skip this. TESTING.md is the single source of truth for how to test this API.

---

## Project Overview

**Stack:** FastAPI + MongoDB (Motor async) + Google Ads API SDK + Meta Graph API
**Auth:** JWT (access: 15min, refresh: 7 days) + Google OAuth for user login
**DB:** MongoDB Atlas — database: `glimmora_reach`
**Deployment:** Railway (backend) + Vercel (frontend)

## Key Files

| File | Purpose |
|---|---|
| `app/main.py` | FastAPI app entry, lifespan, CORS |
| `app/config.py` | All env vars via pydantic-settings |
| `app/database.py` | MongoDB async connection (Motor) |
| `app/core/deps.py` | Auth dependencies, RBAC |
| `app/core/security.py` | JWT encode/decode, bcrypt |
| `app/api/v1/router.py` | Aggregates all routers |
| `app/api/v1/google_ads.py` | All Google Ads routes |
| `app/services/google_ads_service.py` | Google Ads SDK calls |
| `app/services/google_ads_oauth.py` | OAuth URL + token exchange |
| `app/services/ai_insights.py` | Rule-based AI insights engine |
| `app/repositories/google_ads_connection.py` | Per-user Ads token storage |
| `google-ads.yaml` | Google Ads API credentials (no refresh_token — per-user via DB) |
| `app/api/v1/meta_ads.py` | All Meta (Facebook) Ads routes |
| `app/services/meta_ads_service.py` | Meta Graph API calls (async httpx) |
| `app/schemas/meta_ads.py` | Meta Ads request/response schemas |
| `app/repositories/meta_ads.py` | Meta Ads MongoDB persistence |
| `app/repositories/meta_ads_connection.py` | Per-user Meta token storage |
| `.env` | Environment variables |
| `TESTING.md` | Full API testing reference — KEEP THIS UPDATED |

## Environment Variables

```
GOOGLE_ADS_DEVELOPER_TOKEN   — Explorer-level token (test accounts only)
GOOGLE_ADS_REDIRECT_URI      — OAuth callback URI for Ads connection
GOOGLE_CLIENT_ID             — For user login with Google (different client)
GOOGLE_CLIENT_SECRET         — For user login with Google
META_APP_ID                  — Meta (Facebook) App ID
META_APP_SECRET              — Meta App Secret
META_REDIRECT_URI            — OAuth callback URI for Meta Ads connection
META_GRAPH_VERSION           — Graph API version (default: v19.0)
```

## Google Ads OAuth Architecture

Two separate OAuth clients exist:
- **User Login** (`GOOGLE_CLIENT_ID` in `.env`) — signs user into the app
- **Ads API** (`client_id` in `google-ads.yaml`) — connects user's Google Ads account

Per-user refresh tokens are stored in the `ads_connections` MongoDB collection.
The `google-ads.yaml` file does NOT contain a refresh_token — tokens come from DB.

## Meta Ads OAuth Architecture

- **Meta App** (`META_APP_ID` + `META_APP_SECRET` in `.env`) — connects user's Meta Ads account
- OAuth flow: code → short-lived token → **long-lived token (~60 days)**
- Per-user long-lived tokens stored in the `meta_connections` MongoDB collection
- Page Access Tokens (for lead gen) are stored alongside during OAuth and used automatically
- No SDK needed — all calls via `httpx` to Meta Graph API (`https://graph.facebook.com/v19.0`)

## Adding a New Router

1. Create route file in `app/api/v1/`
2. Create matching schema in `app/schemas/`
3. Create repository in `app/repositories/`
4. Create service in `app/services/`
5. Register router in `app/api/v1/router.py`
6. **Update TESTING.md**
