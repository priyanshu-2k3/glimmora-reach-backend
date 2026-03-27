# API Test Results — Full Suite (including Google Ads Live)

**Tested:** 2026-03-27
**Server:** FastAPI + MongoDB Atlas
**Base URL:** `http://localhost:8000/api/v1`
**Test method:** `curl` via bash (`.venv` activated)

---

## Summary Table

| # | Endpoint | Method | Auth | Role | HTTP | Result | Notes |
|---|----------|--------|------|------|------|--------|-------|
| 1 | `/health` | GET | No | — | 200 | ✅ | `{"status":"ok"}` |
| 2 | `/auth/login` | POST | No | — | 200 | ✅ | Returns `access_token`, `refresh_token`, `user` |
| 3 | `/auth/me` | GET | Bearer | Any | 200 | ✅ | Full user profile (snake_case) |
| 4 | `/auth/me/spec` | GET | Bearer | Any | 200 | ✅ | Frontend shape: id, name, role, orgId, avatar (camelCase) |
| 5 | `/auth/register` | POST | No | — | 200 | ✅ | Creates user + returns tokens. Default role: `client` |
| 6 | `/auth/refresh` | POST | No | — | 200 | ✅ | Exchange refresh token → new token pair |
| 7 | `/auth/me` | PATCH | Bearer | Any | 200 | ✅ | Update own profile fields |
| 8 | `/auth/profile` | PUT | Bearer | Any | 200 | ✅ | Same as PATCH /auth/me |
| 9 | `/auth/me/change-password` | POST | Bearer | Any | 200 | ✅ | Verifies current password before updating |
| 10 | `/auth/logout` | POST | Bearer | Any | 200 | ✅ | Stateless — `{"message":"Logged out"}` |
| 11 | `/auth/accept-invite` | POST | No | — | 200 | ✅ | Completes invite registration → returns tokens |
| 12 | `/auth/oauth/google` | GET | No | — | 200 | ✅ | Returns Google OAuth URL for user login |
| 13 | `/organizations` | POST | Bearer | SUPER_ADMIN | 201 | ✅ | Create org, returns `id` (UUID hex) |
| 14 | `/organizations` | GET | Bearer | SUPER_ADMIN | 200 | ✅ | List all orgs with `member_count` |
| 15 | `/organizations/:id` | GET | Bearer | SA / ADMIN | 200 | ✅ | ADMIN restricted to own org |
| 16 | `/organizations/:id` | PUT | Bearer | SA / ADMIN | 200 | ✅ | Update name or is_active |
| 17 | `/organizations/:id/members` | GET | Bearer | SA / ADMIN | 200 | ✅ | List org members |
| 18 | `/users/create-admin` | POST | Bearer | SUPER_ADMIN | 201 | ✅ | Create ADMIN user for org |
| 19 | `/users` | GET | Bearer | SA / ADMIN | 200 | ✅ | SUPER_ADMIN: all; ADMIN: own org |
| 20 | `/users/invite` | POST | Bearer | ADMIN | 201 | ✅ | Returns invite `token`, valid 3 days |
| 21 | `/users/:id/role` | PUT | Bearer | ADMIN | 200 | ✅ | Change role in own org (not ADMIN/SA) |
| 22 | `/users/:id` | DELETE | Bearer | ADMIN | 200 | ✅ | Soft delete — sets `is_active=false` |
| 23 | `/google-ads/oauth/url` | GET | Bearer | Any | 200 | ✅ | Returns Google Ads OAuth URL |
| 24 | `/google-ads/oauth/callback` | GET | No | — | 200 | ✅ | **Tested live** — browser redirected by Google, code exchanged for refresh_token, stored in `ads_connections` DB collection. Response: HTML page "✅ Google Ads Connected!" |
| 25 | `/google-ads/connection` | GET | Bearer | Any | 200 | ✅ | `{"connected":true,"connected_at":"..."}` |
| 26 | `/google-ads/accounts` | GET | Bearer | Any | 200 | ✅ | 3 accounts: `5450854268`, `8478518593`, `9695239839` |
| 27 | `/google-ads/dashboard` | GET | Bearer | Any | 200 | ✅ | 10 campaigns, 0 active (all paused) |
| 28 | `/google-ads/metrics` | GET | Bearer | Any | 200 | ✅ | 10 campaigns returned, days=7 and days=30 both work |
| 29 | `/google-ads/campaigns/live` | GET | Bearer | Any | 200 | ✅ | 10 live campaigns fetched from Ads API |
| 30 | `/google-ads/insights/generate` | POST | Bearer | Any | 200 | ✅ | Runs analysis, 0 insights (campaigns have no activity) |
| 31 | `/google-ads/insights` | GET | Bearer | Any | 200 | ✅ | Returns saved insights from DB |
| 32 | `/google-ads/budgets` | GET | Bearer | Any | 200 | ✅ | Local DB list |
| 33 | `/google-ads/campaigns` | GET | Bearer | Any | 200 | ✅ | Local DB list |
| 34 | `/google-ads/adgroups` | GET | Bearer | Any | 200 | ✅ | Local DB list |
| 35 | `/google-ads/ads` | GET | Bearer | Any | 200 | ✅ | Local DB list |
| 36 | `/google-ads/keywords` | GET | Bearer | Any | 200 | ✅ | Local DB list |
| 37 | `/google-ads/budget` | POST | Bearer | Any | 200 | ✅ | Budget created on accounts `8478518593`, `9695239839` |
| 38 | `/google-ads/campaign` | POST | Bearer | Any | 403 | ⚠️ | See note below |
| 39 | `/google-ads/campaign/:id/status` | PATCH | Bearer | Any | 403 | ⚠️ | See note below |
| 40 | `/google-ads/campaign/:id` | DELETE | Bearer | Any | 403 | ⚠️ | See note below |
| 41 | `/google-ads/adgroup` | POST | Bearer | Any | — | ⚠️ | Blocked by campaign creation issue |
| 42 | `/google-ads/ad` | POST | Bearer | Any | — | ⚠️ | Blocked by campaign creation issue |
| 43 | `/google-ads/keywords` | POST | Bearer | Any | — | ⚠️ | Blocked by campaign creation issue |
| 44 | `/google-ads/connection` | DELETE | Bearer | Any | — | — | Not tested (would disconnect the account) |

---

## Google Ads OAuth Callback — Tested Live

The full OAuth flow was completed end-to-end during this test session:

| Step | What happened | Result |
|------|--------------|--------|
| `GET /google-ads/oauth/url` | Called with SA Bearer token | ✅ Returned full Google authorization URL with `state=69c154ceeb0a5531131fbe7b` |
| Browser opened URL | User selected Google account with Ads access | ✅ Google redirected to callback |
| `GET /google-ads/oauth/callback?code=...&state=...` | Server received auth code from Google | ✅ Exchanged code for `access_token` + `refresh_token` |
| Token stored | `refresh_token` saved to MongoDB `ads_connections` collection | ✅ Linked to `user_id=69c154ceeb0a5531131fbe7b` |
| Browser response | HTML page returned to user | ✅ Showed **"✅ Google Ads Connected! Your account has been linked."** |
| `GET /google-ads/connection` | Verified connection | ✅ `{"connected": true, "connected_at": "2026-03-27T10:23:42.065000"}` |

**Note:** The callback endpoint (`/google-ads/oauth/callback`) cannot be hit directly with curl — it is called by Google's servers as a redirect. The redirect URI `http://localhost:8000/api/v1/google-ads/oauth/callback` must be registered in [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials) for the OAuth client to work.

---

## Google Ads Account Discovery

Three accounts were returned from `/google-ads/accounts`:

| Customer ID | Campaigns | Budget Create | Campaign Create | Type |
|-------------|-----------|---------------|-----------------|------|
| `5450854268` | 10 (all PAUSED) | ❌ Permission denied | ❌ Permission denied | Read-only client account |
| `8478518593` | 0 | ✅ Works | ❌ `OPERATION_NOT_PERMITTED_FOR_CONTEXT` | Manager (MCC) account |
| `9695239839` | 0 | ✅ Works | ❌ `OPERATION_NOT_PERMITTED_FOR_CONTEXT` | Manager (MCC) account |

**Root cause for campaign creation failures:**

- `5450854268` — your Google Ads login has **read-only** access on this account. Budgets and campaigns cannot be created.
- `8478518593` and `9695239839` — these are **Manager (MCC) accounts**. Google Ads does not allow creating campaigns directly on a manager account — campaigns must be created on a regular client (leaf) account underneath it.

**Account hierarchy discovered:**
```
8478518593  (Manager)
└── 3823064817  (Sub-manager — also a manager, no client accounts linked)

9695239839  (Manager — no child accounts)
```

**To fully test campaign/adgroup/ad/keyword creation**, you need one of:
1. A **standard client account** (non-manager) linked under your MCC — create one at [ads.google.com](https://ads.google.com) → Tools → Sub-account manager → Create account
2. Or grant **admin/standard access** to the Google account used in OAuth on account `5450854268`

---

## Live Campaigns Found (customer `5450854268`)

| Campaign ID | Name | Status |
|-------------|------|--------|
| 21013608902 | Search OCR | PAUSED |
| 21030252162 | Performance Max | PAUSED |
| 21032183949 | Performance Max new | PAUSED |
| 21132749433 | TPRM | PAUSED |
| 21188375021 | Search-USA | PAUSED |
| 22103815666 | GRC 2025 | PAUSED |
| 22170208312 | Leads-Display | PAUSED |
| 22179734597 | Performance Max-GCC | PAUSED |
| 22201154569 | GRC/TPRM Search Camp 5th Feb 2025 | PAUSED |
| 22201845283 | GRC Display Ads - 5th Feb 2025 | PAUSED |

All campaigns are paused → metrics show 0 clicks/impressions → AI insights returns 0 insights (no activity to analyze).

---

## How to Run Tests

```bash
# 1. Activate venv and start server
cd D:/BAAREZ/glimmorareachbackend
.venv/Scripts/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Run Python test script
python scripts/test_apis.py
```

---

## curl Reference — All Endpoints

### Health

```bash
curl -s http://localhost:8000/health
# → {"status":"ok"}
```

---

### Authentication

```bash
# Login
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@test.com","password":"SuperAdmin1!"}'

# Get profile
curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN"

# Get profile — frontend spec shape (camelCase)
curl -s http://localhost:8000/api/v1/auth/me/spec \
  -H "Authorization: Bearer TOKEN"

# Register
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Jane","last_name":"Doe","email":"jane@example.com","password":"SecurePass1!"}'

# Refresh token
curl -s -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"REFRESH_TOKEN"}'

# Update profile (PATCH)
curl -s -X PATCH http://localhost:8000/api/v1/auth/me \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"first_name":"Jane","language":"en","timezone":"Asia/Kolkata"}'

# Update profile (PUT)
curl -s -X PUT http://localhost:8000/api/v1/auth/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"first_name":"Jane","last_name":"Doe"}'

# Change password
curl -s -X POST http://localhost:8000/api/v1/auth/me/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"current_password":"OldPass1!","new_password":"NewPass1!"}'

# Logout
curl -s -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer TOKEN"

# Accept invite
curl -s -X POST http://localhost:8000/api/v1/auth/accept-invite \
  -H "Content-Type: application/json" \
  -d '{"token":"INVITE_TOKEN","first_name":"Jane","last_name":"Doe","password":"MemberPass1!"}'

# Google OAuth URL (user login)
curl -s http://localhost:8000/api/v1/auth/oauth/google
```

---

### Organizations

```bash
# Create organization  (SUPER_ADMIN only)
curl -s -X POST http://localhost:8000/api/v1/organizations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SA_TOKEN" \
  -d '{"name":"Acme Corp"}'

# List organizations  (SUPER_ADMIN only)
curl -s http://localhost:8000/api/v1/organizations \
  -H "Authorization: Bearer SA_TOKEN"

# Get organization  (ADMIN: own org only)
curl -s http://localhost:8000/api/v1/organizations/ORG_ID \
  -H "Authorization: Bearer TOKEN"

# Update organization  (ADMIN: own org only)
curl -s -X PUT http://localhost:8000/api/v1/organizations/ORG_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name":"New Name","is_active":true}'

# List org members  (ADMIN: own org only)
curl -s http://localhost:8000/api/v1/organizations/ORG_ID/members \
  -H "Authorization: Bearer TOKEN"
```

---

### Users

```bash
# Create admin user  (SUPER_ADMIN only)
curl -s -X POST http://localhost:8000/api/v1/users/create-admin \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SA_TOKEN" \
  -d '{"first_name":"Org","last_name":"Admin","email":"admin@example.com","password":"AdminPass1!","organization_id":"ORG_ID"}'

# List users  (SUPER_ADMIN: all | ADMIN: own org)
curl -s http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Invite user  (ADMIN only)
curl -s -X POST http://localhost:8000/api/v1/users/invite \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{"email":"member@example.com","role":"CAMPAIGN_MANAGER"}'
# Roles: CAMPAIGN_MANAGER | ANALYTICS | VIEWER

# Update user role  (ADMIN only — own org)
curl -s -X PUT http://localhost:8000/api/v1/users/USER_ID/role \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{"role":"ANALYTICS"}'

# Deactivate user  (ADMIN only — soft delete)
curl -s -X DELETE http://localhost:8000/api/v1/users/USER_ID \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

### Google Ads — OAuth & Connection

```bash
# Step 1: Get OAuth URL
curl -s http://localhost:8000/api/v1/google-ads/oauth/url \
  -H "Authorization: Bearer TOKEN"
# ✅ TESTED — Response:
# {
#   "url": "https://accounts.google.com/o/oauth2/auth?client_id=927358654435-emqpgnna47gdc2ogu92pp7v0t0ld0hmh.apps.googleusercontent.com
#           &redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fv1%2Fgoogle-ads%2Foauth%2Fcallback
#           &response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fadwords
#           &access_type=offline&prompt=consent&state=69c154ceeb0a5531131fbe7b"
# }
# state = user_id of the logged-in user (used to link token to account)

# Step 2: Open URL in browser — NOT a curl call (Google redirects back)
# After granting access, Google calls:
#   GET /api/v1/google-ads/oauth/callback?code=AUTH_CODE&state=USER_ID
# The server exchanges the code for tokens and stores refresh_token in DB.
# ✅ TESTED — Browser showed: "✅ Google Ads Connected!
#                               Your account has been linked. You can close this tab."
# Internally: refresh_token saved to MongoDB collection `ads_connections`
#             document: { user_id, org_id, refresh_token, connected_at }

# Step 3: Verify connection
curl -s http://localhost:8000/api/v1/google-ads/connection \
  -H "Authorization: Bearer TOKEN"
# ✅ TESTED — Response:
# {"connected": true, "connected_at": "2026-03-27T10:23:42.065000"}

# List accessible accounts
curl -s http://localhost:8000/api/v1/google-ads/accounts \
  -H "Authorization: Bearer TOKEN"
# ✅ TESTED — Response:
# {"accounts": ["customers/5450854268", "customers/8478518593", "customers/9695239839"]}

# Disconnect (removes refresh_token from DB)
curl -s -X DELETE http://localhost:8000/api/v1/google-ads/connection \
  -H "Authorization: Bearer TOKEN"
# → {"status": "disconnected"}
```

---

### Google Ads — Analytics (Read-only, Works on all accounts)

```bash
# Dashboard summary (last 30 days)
curl -s "http://localhost:8000/api/v1/google-ads/dashboard?customer_id=5450854268" \
  -H "Authorization: Bearer TOKEN"
# → {total_clicks, total_impressions, total_cost_inr, total_conversions, avg_ctr,
#    campaign_count:10, active_campaigns:0, paused_campaigns:10}

# Campaign metrics (days=1 to 90)
curl -s "http://localhost:8000/api/v1/google-ads/metrics?customer_id=5450854268&days=30" \
  -H "Authorization: Bearer TOKEN"
# → {"metrics":[{campaign_id, campaign_name, campaign_status, clicks, impressions,
#               cost_inr, conversions, ctr}], "count":10}

# Live campaigns from Ads API
curl -s "http://localhost:8000/api/v1/google-ads/campaigns/live?customer_id=5450854268" \
  -H "Authorization: Bearer TOKEN"
# → {"campaigns":[{id, name, status, resource}], "count":10}

# Generate AI insights
curl -s -X POST "http://localhost:8000/api/v1/google-ads/insights/generate?customer_id=5450854268" \
  -H "Authorization: Bearer TOKEN"
# → {"insights":[], "count":0, "generated_at":"..."} (0 insights — campaigns have no activity)

# Get saved insights
curl -s "http://localhost:8000/api/v1/google-ads/insights?customer_id=5450854268" \
  -H "Authorization: Bearer TOKEN"
```

---

### Google Ads — Campaign Building

> **Requires a standard (non-manager) client account with write access.**
> Budget creation works on accounts `8478518593` and `9695239839` (manager accounts).
> Campaign/adgroup/ad/keyword creation requires a leaf client account.

```bash
# Create campaign budget
curl -s -X POST "http://localhost:8000/api/v1/google-ads/budget?customer_id=8478518593" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name":"My Budget","amount_inr":1000,"delivery_method":"STANDARD"}'
# → {status:"created", budget_resource:"customers/.../campaignBudgets/...", db_id}
# delivery_method: STANDARD | ACCELERATED

# List saved budgets (local DB)
curl -s http://localhost:8000/api/v1/google-ads/budgets \
  -H "Authorization: Bearer TOKEN"

# Create campaign  (needs leaf account)
curl -s -X POST "http://localhost:8000/api/v1/google-ads/campaign?customer_id=CLIENT_ACCOUNT_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name":"My Campaign","budget_resource":"customers/.../campaignBudgets/123","channel_type":"SEARCH","status":"PAUSED"}'
# channel_type: SEARCH | DISPLAY | VIDEO | SHOPPING

# Pause / enable campaign
curl -s -X PATCH "http://localhost:8000/api/v1/google-ads/campaign/CAMPAIGN_ID/status?customer_id=CLIENT_ACCOUNT_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"status":"ENABLED"}'

# Delete campaign (permanent)
curl -s -X DELETE "http://localhost:8000/api/v1/google-ads/campaign/CAMPAIGN_ID?customer_id=CLIENT_ACCOUNT_ID" \
  -H "Authorization: Bearer TOKEN"

# Create ad group
curl -s -X POST "http://localhost:8000/api/v1/google-ads/adgroup?customer_id=CLIENT_ACCOUNT_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name":"My Ad Group","campaign_resource":"customers/.../campaigns/789","cpc_bid_inr":10.5,"type_":"SEARCH_STANDARD","status":"PAUSED"}'

# Create responsive search ad
curl -s -X POST "http://localhost:8000/api/v1/google-ads/ad?customer_id=CLIENT_ACCOUNT_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"ad_group_resource":"customers/.../adGroups/101","final_url":"https://example.com","headlines":["Buy Now","Best Deals","Shop Today"],"descriptions":["Get the best products at lowest prices.","Shop from thousands of items online."],"status":"PAUSED"}'
# headlines: 3-30 chars each, min 3 required
# descriptions: max 90 chars each, min 2 required

# Add keywords
curl -s -X POST "http://localhost:8000/api/v1/google-ads/keywords?customer_id=CLIENT_ACCOUNT_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"ad_group_resource":"customers/.../adGroups/101","keywords":["running shoes","buy shoes"],"match_type":"PHRASE"}'
# match_type: BROAD | PHRASE | EXACT
```

---

## Ordered Testing Workflow

### Phase 1 — Auth & Bootstrap
```
POST /auth/login                → SA_TOKEN
GET  /auth/me                   → verify profile
GET  /auth/me/spec              → frontend shape
POST /auth/register             → new user tokens
POST /auth/refresh              → new token pair
```

### Phase 2 — Org & User Setup
```
POST /organizations             → ORG_ID
GET  /organizations             → list
GET  /organizations/:id         → detail
PUT  /organizations/:id         → update name
POST /users/create-admin        → ADMIN user
POST /auth/login                → ADMIN_TOKEN
POST /users/invite              → INVITE_TOKEN
POST /auth/accept-invite        → MEMBER_TOKEN, MEMBER_ID
GET  /users                     → verify members
PUT  /users/:id/role            → change role
DELETE /users/:id               → deactivate
```

### Phase 3 — Google Ads OAuth
```
GET  /google-ads/oauth/url      → open URL in browser
[Complete OAuth in browser]
GET  /google-ads/connection     → {"connected": true}
GET  /google-ads/accounts       → list customer IDs
```

### Phase 4 — Analytics
```
GET  /google-ads/dashboard      → aggregate stats
GET  /google-ads/metrics        → per-campaign metrics
POST /google-ads/insights/generate → AI analysis
GET  /google-ads/insights       → saved insights
GET  /google-ads/campaigns/live → live campaign list
```

### Phase 5 — Campaign Building (needs leaf client account)
```
POST /google-ads/budget         → BUDGET_RESOURCE
POST /google-ads/campaign       → CAMPAIGN_RESOURCE
PATCH /google-ads/campaign/:id/status → pause/enable
POST /google-ads/adgroup        → ADGROUP_RESOURCE
POST /google-ads/ad             → AD_RESOURCE
POST /google-ads/keywords       → keywords added
```

### Phase 6 — Cleanup
```
DELETE /users/:id               → deactivate test user
DELETE /google-ads/connection   → disconnect ads account
```

---

## Role Reference

| Role | Permissions |
|------|-------------|
| `SUPER_ADMIN` | Full access — create orgs, create admins, list all users/orgs |
| `ADMIN` | Manage own org — invite users, change roles, deactivate users |
| `CAMPAIGN_MANAGER` | Full Google Ads access — create/manage campaigns |
| `ANALYTICS` | Read-only — analytics and Google Ads data |
| `VIEWER` / `CLIENT` | Basic profile access only |

---

## Environment Variables

```env
SECRET_KEY=<min 32 chars>
MONGODB_URL=mongodb+srv://...
MONGODB_DB_NAME=glimmora_reach
JWT_ACCESS_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7
SUPER_ADMIN_EMAIL=superadmin@test.com
SUPER_ADMIN_PASSWORD=SuperAdmin1!
GOOGLE_CLIENT_ID=                    # for user login OAuth
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/oauth/google/callback
GOOGLE_ADS_DEVELOPER_TOKEN=          # Explorer-level token
GOOGLE_ADS_REDIRECT_URI=http://localhost:8000/api/v1/google-ads/oauth/callback
FRONTEND_OAUTH_REDIRECT_URI=http://localhost:3000/oauth/callback
INVITE_BASE_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Notes

- **Token expiry:** Access tokens last **15 minutes**. Re-login to get a fresh token before testing.
- **Google Ads OAuth:** The redirect URI `http://localhost:8000/api/v1/google-ads/oauth/callback` must be added to the OAuth client in Google Cloud Console → Credentials before the flow works.
- **AI Insights:** Returns 0 insights when all campaigns are paused with 0 impressions — the rule engine only flags active campaigns with poor metrics.
- **Cost values:** All amounts are in **INR**. Internally converted to Google Ads micros (1 INR = 1,000,000 micros).
- **Campaign creation on MCC:** Google Ads does not allow campaign creation on Manager (MCC) accounts. You need a linked standard client account. Create one at ads.google.com → Tools → Sub-account manager.
- **Soft delete:** `DELETE /users/:id` sets `is_active=false` — user data is preserved in MongoDB.
- **Campaign DELETE:** Permanent hard delete in Google Ads — logs to `deleted_campaigns` collection for audit.
