# Glimmora Reach — Backend API

FastAPI + MongoDB backend for Glimmora Reach — handles authentication, organizations, user management, and full Google Ads campaign management.

---

## Live URLs

| Environment | URL |
|---|---|
| Backend (Railway) | https://glimmora-reach-backend-production.up.railway.app |
| Frontend (Vercel) | https://glimmora-reach-frontend.vercel.app |
| API Docs (local) | http://localhost:8000/docs |
| API Docs (production) | https://glimmora-reach-backend-production.up.railway.app/docs |

---

## Project Structure

```
glimmorareachbackend/
├── app/
│   ├── main.py                       # FastAPI app + lifespan
│   ├── config.py                     # All settings loaded from .env
│   ├── database.py                   # MongoDB async connection (Motor)
│   │
│   ├── api/v1/
│   │   ├── router.py                 # Aggregates all routers
│   │   ├── auth.py                   # Auth + Google OAuth endpoints
│   │   ├── users.py                  # User management endpoints
│   │   ├── organizations.py          # Organization endpoints
│   │   └── google_ads.py             # Google Ads campaign endpoints
│   │
│   ├── schemas/
│   │   ├── auth.py                   # Auth request/response shapes
│   │   ├── user.py                   # User shapes
│   │   ├── organization.py           # Org shapes
│   │   ├── common.py                 # Shared shapes
│   │   └── google_ads.py             # Google Ads request/response shapes
│   │
│   ├── models/
│   │   ├── user.py                   # User MongoDB document shape
│   │   ├── organization.py           # Org document shape
│   │   ├── invitation.py             # Invite document shape
│   │   └── constants.py              # Roles, enums
│   │
│   ├── repositories/
│   │   ├── user.py                   # User DB queries
│   │   ├── organization.py           # Org DB queries
│   │   ├── invitation.py             # Invite DB queries
│   │   └── google_ads.py             # Google Ads DB queries
│   │
│   ├── services/
│   │   ├── auth.py                   # Auth logic (register, login, JWT)
│   │   ├── oauth_google.py           # Google OAuth token exchange
│   │   ├── user_service.py           # User business logic
│   │   ├── org_service.py            # Org business logic
│   │   └── google_ads_service.py     # Google Ads SDK logic
│   │
│   └── core/
│       ├── deps.py                   # FastAPI deps: JWT auth, RBAC
│       └── security.py               # JWT encode/decode, bcrypt
│
├── google-ads.yaml                   # Google Ads SDK credentials (do not commit)
├── .env                              # Environment variables (do not commit)
├── requirements.txt                  # Python dependencies
├── Procfile                          # Railway start command
└── seed.py                           # Seed super admin user
```

---

## All Features & Endpoints

### Auth — `/api/v1/auth`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register` | No | Register new user, returns JWT tokens |
| POST | `/login` | No | Login with email + password |
| POST | `/refresh` | No | Get new tokens using refresh token |
| POST | `/logout` | No | Client-side logout |
| GET | `/me` | Yes | Get current user profile |
| PATCH | `/me` | Yes | Update name, avatar, language |
| DELETE | `/me` | Yes | Delete own account |
| POST | `/me/change-password` | Yes | Change password |
| PUT | `/profile` | Yes | Full profile update |
| GET | `/me/spec` | Yes | Profile in spec shape (id, name, role, orgId) |
| POST | `/accept-invite` | No | Accept org invite, registers and logs in |
| GET | `/oauth/google` | No | Returns Google OAuth URL |
| GET | `/oauth/google/callback` | No | Callback — exchanges code, issues JWT, redirects to frontend |

### Users — `/api/v1/users`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Admin | List all users |
| GET | `/{user_id}` | Yes | Get user by ID |
| PATCH | `/{user_id}` | Admin | Update user |
| DELETE | `/{user_id}` | Admin | Delete user |

### Organizations — `/api/v1/organizations`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/` | Yes | Create organization |
| GET | `/` | Yes | List organizations |
| GET | `/{org_id}` | Yes | Get organization |
| PATCH | `/{org_id}` | Yes | Update organization |
| DELETE | `/{org_id}` | Admin | Delete organization |
| POST | `/{org_id}/invite` | Yes | Invite user to org by email |

### Google Ads — `/api/v1/google-ads`

> All endpoints require `Authorization: Bearer <access_token>`.
> Every write operation also saves a record to MongoDB.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/accounts` | List accessible Google Ads accounts |
| POST | `/budget?customer_id=` | Create campaign budget |
| GET | `/budgets` | All budgets saved in MongoDB |
| POST | `/campaign?customer_id=` | Create campaign |
| GET | `/campaigns` | All campaigns saved in MongoDB |
| GET | `/campaigns/live?customer_id=` | Live fetch from Google Ads |
| DELETE | `/campaign/{id}?customer_id=` | Delete campaign |
| POST | `/adgroup?customer_id=` | Create ad group |
| GET | `/adgroups` | All ad groups saved in MongoDB |
| POST | `/ad?customer_id=` | Create responsive search ad |
| GET | `/ads` | All ads saved in MongoDB |
| POST | `/keywords?customer_id=` | Add keywords to ad group |
| GET | `/keywords` | All keywords saved in MongoDB |

---

## MongoDB Collections

| Collection | Created by |
|---|---|
| `users` | Register / Google OAuth |
| `organizations` | Create org |
| `invitations` | Invite user |
| `ads_budgets` | POST /google-ads/budget |
| `ads_campaigns` | POST /google-ads/campaign |
| `ads_adgroups` | POST /google-ads/adgroup |
| `ads_ads` | POST /google-ads/ad |
| `ads_keywords` | POST /google-ads/keywords |
| `ads_deleted_campaigns` | DELETE /google-ads/campaign/{id} |

---

## Local Development Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure `.env`

```env
APP_ENV=development
SECRET_KEY=your-secret-key-min-32-chars-change-in-production

MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/glimmora_reach
MONGODB_DB_NAME=glimmora_reach

JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/oauth/google/callback
FRONTEND_OAUTH_REDIRECT_URI=http://localhost:3000/oauth/callback

CORS_ORIGINS=http://localhost:3000,http://localhost:5173

GOOGLE_ADS_DEVELOPER_TOKEN=your-developer-token
GOOGLE_ADS_REFRESH_TOKEN=your-refresh-token
```

### 3. Configure `google-ads.yaml`

```yaml
developer_token: YOUR_DEVELOPER_TOKEN
client_id: YOUR_GOOGLE_CLIENT_ID
client_secret: YOUR_GOOGLE_CLIENT_SECRET
refresh_token: YOUR_REFRESH_TOKEN
use_proto_plus: True
```

### 4. Seed super admin

```bash
python seed.py
```

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

---

## Google Ads — Full Workflow

Follow this order — each step needs the `resource` value from the previous step:

```
1. POST /auth/login                         → copy access_token
2. GET  /google-ads/accounts                → copy customer_id (number, no dashes)
3. POST /google-ads/budget                  → copy budget_resource
4. POST /google-ads/campaign                → copy campaign_resource
5. POST /google-ads/adgroup                 → copy ad_group_resource
6. POST /google-ads/keywords                → adds keywords to ad group
7. POST /google-ads/ad                      → creates the search ad
8. GET  /google-ads/campaigns/live          → verify everything on Google
```

### Step-by-step request bodies

**Step 3 — Create Budget**
```json
{
  "name": "My Budget",
  "amount_inr": 500,
  "delivery_method": "STANDARD"
}
```

**Step 4 — Create Campaign**
```json
{
  "name": "My Campaign",
  "budget_resource": "customers/2999904400/campaignBudgets/123456",
  "channel_type": "SEARCH",
  "status": "PAUSED"
}
```
> Use `"status": "PAUSED"` while testing so it does not go live.

**Step 5 — Create Ad Group**
```json
{
  "name": "My Ad Group",
  "campaign_resource": "customers/2999904400/campaigns/987654",
  "cpc_bid_inr": 10,
  "type_": "SEARCH_STANDARD",
  "status": "ENABLED"
}
```

**Step 6 — Add Keywords**
```json
{
  "ad_group_resource": "customers/2999904400/adGroups/111222333",
  "keywords": ["buy shoes online", "best running shoes", "sports shoes"],
  "match_type": "BROAD"
}
```

**Step 7 — Create Responsive Search Ad**
```json
{
  "ad_group_resource": "customers/2999904400/adGroups/111222333",
  "final_url": "https://yoursite.com",
  "headlines": ["Buy Shoes Online", "Best Running Shoes", "Free Shipping Today"],
  "descriptions": [
    "Shop top-quality running shoes at the best prices.",
    "Huge collection of sports shoes. Order now!"
  ],
  "status": "ENABLED"
}
```

---

## Production Deployment (Railway)

### Step 1 — Set environment variables in Railway

Railway dashboard → your service → **Variables** → add each one:

```
APP_ENV=production
SECRET_KEY=<strong-random-min-32-char-key>
MONGODB_URL=<your-atlas-connection-string>
MONGODB_DB_NAME=glimmora_reach

GOOGLE_CLIENT_ID=927358654435-gphh3qlp9dk9db8s5fo48n17fllajhu4.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=<your-secret>
GOOGLE_REDIRECT_URI=https://glimmora-reach-backend-production.up.railway.app/api/v1/auth/oauth/google/callback
FRONTEND_OAUTH_REDIRECT_URI=https://glimmora-reach-frontend.vercel.app/oauth/callback
CORS_ORIGINS=https://glimmora-reach-frontend.vercel.app

GOOGLE_ADS_DEVELOPER_TOKEN=JajlMxlEDxbSXR6UCHNlwA
GOOGLE_ADS_REFRESH_TOKEN=<your-refresh-token>
```

### Step 2 — Update Google Cloud Console

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. **APIs & Services → Credentials → your OAuth 2.0 Client ID**
3. Under **Authorized redirect URIs** — add:
   ```
   https://glimmora-reach-backend-production.up.railway.app/api/v1/auth/oauth/google/callback
   ```
4. Under **Authorized JavaScript origins** — add:
   ```
   https://glimmora-reach-frontend.vercel.app
   ```
5. Click **Save**

### Step 3 — Handle google-ads.yaml on Railway

`google-ads.yaml` is not committed to git. Create `build.sh` in the repo root:

```bash
#!/bin/bash
cat > google-ads.yaml <<EOF
developer_token: ${GOOGLE_ADS_DEVELOPER_TOKEN}
client_id: ${GOOGLE_CLIENT_ID}
client_secret: ${GOOGLE_CLIENT_SECRET}
refresh_token: ${GOOGLE_ADS_REFRESH_TOKEN}
use_proto_plus: True
EOF
```

Update `Procfile`:
```
web: bash build.sh && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Step 4 — Deploy

```bash
git add .
git commit -m "deploy: production config"
git push origin main
```

Railway auto-deploys on push to `main`. Check **Deployments → Logs** in the dashboard.

---

## Common Errors

| Error | Fix |
|---|---|
| `401 Unauthorized` | JWT expired — call `/auth/login` again |
| `OAuth is not configured` | Add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to Railway Variables |
| `Redirect URI mismatch` | Add the production callback URL to Google Cloud Console |
| `CORS blocked on frontend` | Set `CORS_ORIGINS` to your Vercel frontend URL in Railway Variables |
| `google-ads.yaml not found` | Add `build.sh` and update `Procfile` (see Step 3 above) |
| `Invalid developer token` | Your token only works with test accounts — apply for Basic Access in Google Ads API Center |
| `Customer not found` | Use the exact `customer_id` returned from `GET /google-ads/accounts` |

---

## Local vs Production Config Reference

| Variable | Local Value | Production Value |
|---|---|---|
| `APP_ENV` | `development` | `production` |
| `GOOGLE_REDIRECT_URI` | `http://localhost:8000/api/v1/auth/oauth/google/callback` | `https://glimmora-reach-backend-production.up.railway.app/api/v1/auth/oauth/google/callback` |
| `FRONTEND_OAUTH_REDIRECT_URI` | `http://localhost:3000/oauth/callback` | `https://glimmora-reach-frontend.vercel.app/oauth/callback` |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | `https://glimmora-reach-frontend.vercel.app` |
