# API Testing Reference — Glimmora Reach Backend

Base URL: `http://localhost:8000/api/v1`

---

## Route Reference Table

### Auth Routes — `/api/v1/auth`

| Route | Method | Headers | Request Params | Response | What It Does |
|---|---|---|---|---|---|
| `/auth/register` | POST | None | `first_name`, `last_name`, `email`, `password`, `role` (optional, default: client), `language` (optional) | `access_token`, `refresh_token`, `token_type`, `expires_in`, `user` | Registers a new user. Returns JWT tokens immediately. |
| `/auth/login` | POST | None | `email`, `password` | `access_token`, `refresh_token`, `token_type`, `expires_in`, `user` | Logs in with email + password. Returns JWT tokens. |
| `/auth/refresh` | POST | None | `refresh_token` | `access_token`, `refresh_token`, `token_type`, `expires_in`, `user` | Exchanges a valid refresh token for a new access token. |
| `/auth/me` | GET | `Authorization: Bearer <token>` | None | `id`, `first_name`, `last_name`, `email`, `role`, `profile_picture`, `language`, `timezone`, `email_verified`, `is_active`, `organization_ids`, `created_at`, `last_login_at` | Returns the currently logged-in user's profile. |
| `/auth/me` | PATCH | `Authorization: Bearer <token>` | `first_name` (opt), `last_name` (opt), `profile_picture` (opt), `language` (opt), `timezone` (opt) | Updated `UserProfile` | Partially updates the current user's profile. |
| `/auth/me` | DELETE | `Authorization: Bearer <token>` | None | `message: "Account deleted"` | Deletes the current user's account permanently. |
| `/auth/me/change-password` | POST | `Authorization: Bearer <token>` | `current_password`, `new_password` (8-128 chars) | `message: "Password updated"` | Changes password after verifying current password. |
| `/auth/me/spec` | GET | `Authorization: Bearer <token>` | None | `id`, `name`, `email`, `role`, `orgId`, `avatar`, `createdAt` | Returns current user in frontend-spec shape (camelCase). |
| `/auth/logout` | POST | None | None | `message: "Logged out"` | Stateless logout — client should clear token. No server invalidation. |
| `/auth/accept-invite` | POST | None | `token`, `first_name`, `last_name`, `password` | `access_token`, `refresh_token`, `user` | Completes registration from an org invite link. Logs user in. |
| `/auth/oauth/google` | GET | None | `state` (optional query param) | `url: str` | Returns Google OAuth URL for signing into the app with Google. Open in browser. |
| `/auth/oauth/google/callback` | GET | None | `code` (query), `redirect` (query, default true) | `LoginResponse` or redirect to frontend | Google redirects here after user grants access. Exchanges code for tokens. |

---

### User Management Routes — `/api/v1/users`

| Route | Method | Headers | Request Params | Response | What It Does |
|---|---|---|---|---|---|
| `/users/create-admin` | POST | `Authorization: Bearer <token>` (SUPER_ADMIN only) | `first_name`, `last_name`, `email`, `password`, `organization_id` | User object | Creates an ADMIN user and assigns them to an org. SUPER_ADMIN only. |
| `/users/invite` | POST | `Authorization: Bearer <token>` (ADMIN only) | `email`, `role` (CAMPAIGN_MANAGER \| ANALYTICS \| VIEWER) | `id`, `email`, `role`, `status`, `expires_at` | Sends an invite to a user to join the ADMIN's organization. |
| `/users` | GET | `Authorization: Bearer <token>` (ADMIN or SUPER_ADMIN) | None | Array of user objects | Lists users. SUPER_ADMIN sees all; ADMIN sees only their org. |
| `/users/{user_id}/role` | PUT | `Authorization: Bearer <token>` (ADMIN only) | `role` (body) | Updated user object | Changes a user's role. Cannot set SUPER_ADMIN or ADMIN via this route. |
| `/users/{user_id}` | DELETE | `Authorization: Bearer <token>` (ADMIN only) | None | `message: "User deactivated"` | Soft-deletes (deactivates) a user in the ADMIN's org. |

---

### Organization Routes — `/api/v1/organizations`

| Route | Method | Headers | Request Params | Response | What It Does |
|---|---|---|---|---|---|
| `/organizations` | POST | `Authorization: Bearer <token>` (SUPER_ADMIN only) | `name` | Organization object | Creates a new organization. SUPER_ADMIN only. |
| `/organizations` | GET | `Authorization: Bearer <token>` (SUPER_ADMIN only) | None | Array of organization objects | Lists all organizations in the system. |
| `/organizations/{org_id}` | GET | `Authorization: Bearer <token>` (SUPER_ADMIN or ADMIN own org) | None | `id`, `name`, `created_by`, `is_active`, `created_at`, `updated_at`, `member_count` | Gets a single organization by ID. |
| `/organizations/{org_id}` | PUT | `Authorization: Bearer <token>` (SUPER_ADMIN or ADMIN own org) | `name` (opt), `is_active` (opt) | Updated organization object | Updates org name or active status. |
| `/organizations/{org_id}/members` | GET | `Authorization: Bearer <token>` (SUPER_ADMIN or ADMIN own org) | None | Array of user objects | Lists all members (users) in a specific organization. |

---

### Google Ads Routes — `/api/v1/google-ads`

> All routes marked **[Ads Auth Required]** need the user to have connected their Google Ads account first via the OAuth flow.

| Route | Method | Headers | Request Params | Response | What It Does |
|---|---|---|---|---|---|
| `/google-ads/oauth/url` | GET | `Authorization: Bearer <token>` | None | `url: str` | Returns Google OAuth URL scoped to `adwords`. Open this URL in a browser to connect Google Ads account. |
| `/google-ads/oauth/callback` | GET | None | `code` (query), `state` (query = user_id), `error` (query) | HTML page | Google redirects here after user grants Ads access. Stores refresh token in DB linked to user. |
| `/google-ads/connection` | GET | `Authorization: Bearer <token>` | None | `connected: bool`, `connected_at: str` | Checks if the current user has a connected Google Ads account. |
| `/google-ads/connection` | DELETE | `Authorization: Bearer <token>` | None | `status: "disconnected"` | Removes the stored Google Ads refresh token for the current user. |
| `/google-ads/accounts` | GET | `Authorization: Bearer <token>` **[Ads Auth Required]** | None | `accounts: list[str]` (resource names) | Lists all Google Ads accounts accessible to the connected token. |
| `/google-ads/dashboard` | GET | `Authorization: Bearer <token>` **[Ads Auth Required]** | `customer_id` (query) | `total_clicks`, `total_impressions`, `total_cost_inr`, `total_conversions`, `avg_ctr`, `campaign_count`, `active_campaigns`, `paused_campaigns` | Aggregated dashboard stats for a specific Google Ads account. |
| `/google-ads/metrics` | GET | `Authorization: Bearer <token>` **[Ads Auth Required]** | `customer_id` (query), `days` (query, 1-90, default 30) | `metrics: list`, `count: int` | Fetches and stores per-campaign metrics for the last N days. Each metric includes clicks, impressions, cost_inr, conversions, ctr. |
| `/google-ads/insights/generate` | POST | `Authorization: Bearer <token>` **[Ads Auth Required]** | `customer_id` (query) | `insights: list`, `count`, `generated_at` | Runs rule-based AI analysis on latest metrics. Returns insights with type (LOW_CTR, ZERO_CONVERSIONS, etc.) and severity (INFO, WARNING, CRITICAL). |
| `/google-ads/insights` | GET | `Authorization: Bearer <token>` **[Ads Auth Required]** | `customer_id` (query) | `insights: list`, `count`, `generated_at` | Returns the last saved insights from DB without re-running analysis. |
| `/google-ads/budget` | POST | `Authorization: Bearer <token>` **[Ads Auth Required]** | `customer_id` (query) + body: `name`, `amount_inr`, `delivery_method` (STANDARD\|ACCELERATED) | `status`, `budget_resource`, `db_id` | Creates a campaign budget in Google Ads. Converts INR to micros (1 INR = 1,000,000 micros). |
| `/google-ads/budgets` | GET | `Authorization: Bearer <token>` | None | `budgets: list` | Lists all budgets saved in MongoDB (no Google API call). |
| `/google-ads/campaign` | POST | `Authorization: Bearer <token>` **[Ads Auth Required]** | `customer_id` (query) + body: `name`, `budget_resource`, `channel_type` (SEARCH\|DISPLAY\|VIDEO\|SHOPPING), `status` (ENABLED\|PAUSED) | `status`, `campaign_resource`, `db_id` | Creates a campaign in Google Ads linked to a budget resource. Default status: PAUSED. |
| `/google-ads/campaign/{campaign_id}/status` | PATCH | `Authorization: Bearer <token>` **[Ads Auth Required]** | `customer_id` (query) + body: `status` (ENABLED\|PAUSED) | Updated campaign object | Pauses or enables an existing campaign. |
| `/google-ads/campaigns/live` | GET | `Authorization: Bearer <token>` **[Ads Auth Required]** | `customer_id` (query) | `campaigns: list`, `count` | Fetches live campaign list directly from Google Ads API. Each item: id, name, status, resource. |
| `/google-ads/campaigns` | GET | `Authorization: Bearer <token>` | None | `campaigns: list` | Lists all campaigns saved in MongoDB (no Google API call). |
| `/google-ads/campaign/{campaign_id}` | DELETE | `Authorization: Bearer <token>` **[Ads Auth Required]** | `customer_id` (query) | `status`, `campaign_id` | Permanently removes a campaign from Google Ads. Logs in deleted_campaigns collection. |
| `/google-ads/adgroup` | POST | `Authorization: Bearer <token>` **[Ads Auth Required]** | `customer_id` (query) + body: `name`, `campaign_resource`, `cpc_bid_inr`, `type_` (SEARCH_STANDARD), `status` (ENABLED\|PAUSED) | `status`, `ad_group_resource`, `db_id` | Creates an ad group inside a campaign. CPC bid converts INR to micros. |
| `/google-ads/adgroups` | GET | `Authorization: Bearer <token>` | None | `adgroups: list` | Lists all ad groups saved in MongoDB. |
| `/google-ads/ad` | POST | `Authorization: Bearer <token>` **[Ads Auth Required]** | `customer_id` (query) + body: `ad_group_resource`, `final_url`, `headlines` (min 3, max 30 chars each), `descriptions` (min 2, max 90 chars each), `status` | `status`, `ad_resource`, `db_id` | Creates a Responsive Search Ad (RSA) inside an ad group. |
| `/google-ads/ads` | GET | `Authorization: Bearer <token>` | None | `ads: list` | Lists all ads saved in MongoDB. |
| `/google-ads/keywords` | POST | `Authorization: Bearer <token>` **[Ads Auth Required]** | `customer_id` (query) + body: `ad_group_resource`, `keywords: list[str]`, `match_type` (BROAD\|PHRASE\|EXACT) | `status`, `keywords_added`, `db_id` | Adds keywords to an ad group with specified match type. |
| `/google-ads/keywords` | GET | `Authorization: Bearer <token>` | None | `keywords: list` | Lists all keywords saved in MongoDB. |

---

### Health

| Route | Method | Headers | Request Params | Response | What It Does |
|---|---|---|---|---|---|
| `/health` | GET | None | None | `status: "ok"` | Server health check. No auth required. |

---

## Testing Order

Run in this exact sequence. Each step depends on the one before it.

### Phase 1 — Bootstrap (one time only)

```
1.  GET  /health                          → verify server is running
2.  POST /auth/register                   → create your first user (role: super_admin or omit)
    OR run: python seed.py                → creates SUPER_ADMIN from .env
3.  POST /auth/login                      → get access_token + refresh_token
    SAVE: access_token as $TOKEN
```

### Phase 2 — Organization + Team Setup

```
4.  POST /organizations                   → create org         [SUPER_ADMIN]
    SAVE: org id as $ORG_ID
5.  POST /users/create-admin              → create an ADMIN for the org [SUPER_ADMIN]
    SAVE: admin credentials
6.  POST /auth/login                      → login as ADMIN
    SAVE: admin access_token as $ADMIN_TOKEN
7.  POST /users/invite                    → invite a team member [ADMIN]
8.  POST /auth/accept-invite              → accept invite + register [new user]
9.  GET  /organizations/{org_id}/members  → verify team is set up
```

### Phase 3 — Connect Google Ads Account

```
10. GET  /google-ads/oauth/url            → get OAuth URL      [any logged-in user]
    ACTION: open the URL in browser, sign in with Google account that owns Ads account
    ACTION: grant permission → browser shows "Google Ads Connected"
11. GET  /google-ads/connection           → verify connected: true
12. GET  /google-ads/accounts             → list accessible Ads accounts
    SAVE: customer_id (strip "customers/" prefix from resource name)
    Example: "customers/1234567890" → customer_id = "1234567890"
```

### Phase 4 — Campaign Building (in order, each step needs previous result)

```
13. POST /google-ads/budget               → create budget
    body: { "name": "Test Budget", "amount_inr": 500, "delivery_method": "STANDARD" }
    SAVE: budget_resource (e.g. "customers/123/campaignBudgets/456")

14. POST /google-ads/campaign             → create campaign
    body: { "name": "Test Campaign", "budget_resource": "<from step 13>",
            "channel_type": "SEARCH", "status": "PAUSED" }
    SAVE: campaign_resource (e.g. "customers/123/campaigns/789")

15. POST /google-ads/adgroup              → create ad group
    body: { "name": "Test AdGroup", "campaign_resource": "<from step 14>",
            "cpc_bid_inr": 10, "type_": "SEARCH_STANDARD", "status": "ENABLED" }
    SAVE: ad_group_resource (e.g. "customers/123/adGroups/101")

16. POST /google-ads/ad                   → create responsive search ad
    body: { "ad_group_resource": "<from step 15>",
            "final_url": "https://yoursite.com",
            "headlines": ["Buy Now", "Best Deals", "Shop Today"],
            "descriptions": ["Get the best products at great prices.", "Shop our full range now."],
            "status": "ENABLED" }

17. POST /google-ads/keywords             → add keywords
    body: { "ad_group_resource": "<from step 15>",
            "keywords": ["buy shoes", "running shoes", "cheap shoes"],
            "match_type": "BROAD" }
```

### Phase 5 — Analytics + AI Insights

```
18. GET  /google-ads/campaigns/live       → verify campaigns are live on Google
19. GET  /google-ads/metrics              → fetch last 30 days metrics
    query: customer_id=<your_id>&days=30
20. POST /google-ads/insights/generate    → run AI analysis on metrics
    query: customer_id=<your_id>
21. GET  /google-ads/insights             → read saved insights
22. GET  /google-ads/dashboard            → full dashboard stats
```

### Phase 6 — Campaign Management

```
23. PATCH /google-ads/campaign/{id}/status → pause/enable campaign
    body: { "status": "ENABLED" }
24. GET   /google-ads/campaigns           → verify in DB
25. GET   /google-ads/budgets             → verify budgets in DB
26. GET   /google-ads/adgroups            → verify ad groups in DB
27. GET   /google-ads/ads                 → verify ads in DB
28. GET   /google-ads/keywords            → verify keywords in DB
```

### Phase 7 — Cleanup / Disconnect

```
29. DELETE /google-ads/campaign/{id}      → delete a campaign from Google Ads
30. DELETE /google-ads/connection         → disconnect Google Ads account
31. GET    /google-ads/connection         → verify connected: false
```

---

## Quick Reference — Common Values

| Field | Example Value | Notes |
|---|---|---|
| `customer_id` | `1234567890` | No dashes. Strip "customers/" prefix from account resource name |
| `budget_resource` | `customers/123/campaignBudgets/456` | Returned from POST /budget |
| `campaign_resource` | `customers/123/campaigns/789` | Returned from POST /campaign |
| `ad_group_resource` | `customers/123/adGroups/101` | Returned from POST /adgroup |
| `channel_type` | `SEARCH` | SEARCH, DISPLAY, VIDEO, SHOPPING |
| `match_type` | `BROAD` | BROAD, PHRASE, EXACT |
| `delivery_method` | `STANDARD` | STANDARD, ACCELERATED |
| `role` | `campaign_manager` | super_admin, admin, campaign_manager, analyst, client |

---

## Role Permissions Summary

| Role | Can Do |
|---|---|
| `SUPER_ADMIN` | Everything — create orgs, create admins, list all users/orgs |
| `ADMIN` | Manage own org — invite users, change roles, view members |
| `CAMPAIGN_MANAGER` | Campaign operations (Google Ads features) |
| `ANALYST` | Read-only on analytics and reports |
| `CLIENT` | Basic access |
