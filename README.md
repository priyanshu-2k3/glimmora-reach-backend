# Glimmora Reach Backend

FastAPI + MongoDB API for Glimmora Reach (Campaign Engine): **Auth**, **Organizations**, and **User management** (invites, roles, deactivate). Aligned with `backend-api-spec.md`.

---

## Run locally

### 1. Virtual environment and dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. MongoDB

Start MongoDB (e.g. Docker):

```bash
docker run -d -p 27017:27017 --name mongo mongo:7
```

Or use a local MongoDB instance. Default connection: `mongodb://localhost:27017`.

**Redis** is not required (optional for future rate limiting).

### 3. Environment

Copy `.env.example` to `.env` and set at least:

- `SECRET_KEY` — long random string (JWT + app secret)
- `MONGODB_URL` — e.g. `mongodb://localhost:27017`
- `MONGODB_DB_NAME` — e.g. `glimmora_reach`
- For **Super Admin seed**: `SUPER_ADMIN_EMAIL`, `SUPER_ADMIN_PASSWORD`
- For **Google OAuth**: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`

### 4. Seed Super Admin (one-time)

Create the first Super Admin user (required for creating organizations and admins):

```bash
python seed.py
```

Ensure `SUPER_ADMIN_EMAIL` and `SUPER_ADMIN_PASSWORD` are set in `.env`. If a user with that email already exists, the script exits without changes.

### 5. Start the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **API base:** http://localhost:8000  
- **Swagger UI:** http://localhost:8000/docs  
- **ReDoc:** http://localhost:8000/redoc  
- **Health:** http://localhost:8000/health  

---

## How to test everything

Use **Swagger UI** at http://localhost:8000/docs, or the `curl` examples below. Replace `BASE=http://localhost:8000/api/v1` and `TOKEN=...` with your access token where needed.

### 1. Health

```bash
curl -s http://localhost:8000/health
# {"status":"ok"}
```

### 2. Auth

**Register** (optional; you can also use seed + login for Super Admin)

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Test","last_name":"User","email":"test@example.com","password":"Password1!"}'
```

Response includes `access_token`, `refresh_token`, `expires_in`, and optionally `user` (id, name, email, role, orgId, avatar, createdAt).

**Login**

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"YOUR_SUPER_ADMIN_EMAIL","password":"YOUR_SUPER_ADMIN_PASSWORD"}'
```

Save `access_token` from the response for the next steps.

**Get current user (profile)**

```bash
curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Get current user in spec shape** (id, name, role, orgId, avatar, createdAt)

```bash
curl -s http://localhost:8000/api/v1/auth/me/spec \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Update profile** (PUT)

```bash
curl -s -X PUT http://localhost:8000/api/v1/auth/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Admin","last_name":"User","language":"en"}'
```

**Change password**

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/me/change-password \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"current_password":"OLD","new_password":"NewPassword1!"}'
```

**Refresh tokens**

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"YOUR_REFRESH_TOKEN"}'
```

**Logout** (client clears token; no server-side invalidation)

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Accept invite** (after receiving an invite token)

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/accept-invite \
  -H "Content-Type: application/json" \
  -d '{"token":"INVITE_TOKEN","first_name":"Jane","last_name":"Doe","password":"Password1!"}'
```

Returns same shape as login (tokens + user).

**Google OAuth**

- Open in browser: `http://localhost:8000/api/v1/auth/oauth/google`
- After Google login you are redirected to the callback; with default `redirect=true` you get tokens in the URL fragment at `FRONTEND_OAUTH_REDIRECT_URI`.

### 3. Organizations (Super Admin)

Use the **Super Admin** token from seed/login.

**Create organization**

```bash
curl -s -X POST http://localhost:8000/api/v1/organizations \
  -H "Authorization: Bearer SUPER_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme Corp"}'
```

Save the returned `id` (UUID) for creating an admin and for invite flow.

**List organizations**

```bash
curl -s http://localhost:8000/api/v1/organizations \
  -H "Authorization: Bearer SUPER_ADMIN_TOKEN"
```

**Get one organization**

```bash
curl -s http://localhost:8000/api/v1/organizations/ORG_ID \
  -H "Authorization: Bearer SUPER_ADMIN_TOKEN"
```

**Update organization**

```bash
curl -s -X PUT http://localhost:8000/api/v1/organizations/ORG_ID \
  -H "Authorization: Bearer SUPER_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme Inc","is_active":true}'
```

### 4. User management

**Create Admin** (Super Admin only)

```bash
curl -s -X POST http://localhost:8000/api/v1/users/create-admin \
  -H "Authorization: Bearer SUPER_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Org","last_name":"Admin","email":"admin@acme.com","password":"AdminPass1!","organization_id":"ORG_ID"}'
```

Use the `organization_id` from the organization you created.

**Invite user** (Admin only; use the new Admin’s token)

```bash
curl -s -X POST http://localhost:8000/api/v1/users/invite \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"member@acme.com","role":"CAMPAIGN_MANAGER"}'
```

Allowed `role`: `CAMPAIGN_MANAGER`, `ANALYTICS`, or `VIEWER`. Response includes `token` for the invite link.

**List users**

- **Super Admin:** all users  
  `GET /api/v1/users` with Super Admin token  
- **Admin:** users in own org only  
  `GET /api/v1/users` with Admin token  

```bash
curl -s http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Update user role** (Admin only; user must be in same org)

```bash
curl -s -X PUT http://localhost:8000/api/v1/users/USER_ID/role \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"VIEWER"}'
```

**Deactivate user** (Admin only; soft delete)

```bash
curl -s -X DELETE http://localhost:8000/api/v1/users/USER_ID \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 5. Full flow (summary)

1. **Seed:** `python seed.py` (set `SUPER_ADMIN_EMAIL`, `SUPER_ADMIN_PASSWORD` in `.env`).
2. **Login as Super Admin:** `POST /api/v1/auth/login` → get `access_token`.
3. **Create org:** `POST /api/v1/organizations` with body `{"name":"My Org"}` → get `id`.
4. **Create Admin:** `POST /api/v1/users/create-admin` with `organization_id` and admin email/password.
5. **Login as Admin:** `POST /api/v1/auth/login` with admin credentials.
6. **Invite user:** `POST /api/v1/users/invite` with email and `role` (e.g. `CAMPAIGN_MANAGER`).
7. **Accept invite:** Use the invite `token` in `POST /api/v1/auth/accept-invite` with name and password → user is created and logged in.
8. **List users:** As Admin, `GET /api/v1/users`; as Super Admin, same endpoint returns all users.
9. **Update role / Deactivate:** `PUT /api/v1/users/:id/role` and `DELETE /api/v1/users/:id` with Admin token.

---

## Automated API tests

With the server running, you can run all API tests and get a table:

```bash
python scripts/test_apis.py
```

This hits health, auth (login, register, me, profile, change-password, logout, refresh, accept-invite), organizations (create, list, get, update), and users (create-admin, invite, list, update role, deactivate) in workflow order. Results are printed and exit code is 0 only if all pass.

- **CMD + curl:** From Command Prompt run `scripts\test_apis_curl.bat` to hit every API with `curl` and print a results table (server + seed required).

See **`API_TEST_RESULTS.md`** for the full results table, what each API does, and example curl/PowerShell commands.

---

## Project layout

- `app/api/v1/` — auth, organizations, users routers  
- `app/core/` — config, security (JWT, password), dependencies (get_current_user, require_roles)  
- `app/models/` — user, organization, invitation, constants (roles)  
- `app/repositories/` — user, organization, invitation  
- `app/schemas/` — Pydantic request/response (auth, organization, user)  
- `app/services/` — auth, org, user  
- `seed.py` — create Super Admin user  
- `backend-api-spec.md` — full API spec  
- `AUTH_REPORT.md` — auth routes summary  

---

## Roles (spec)

- **SUPER_ADMIN** — global; creates orgs and admins; sees all orgs/users.  
- **ADMIN** — one org; invites users; manages org and team (list, role, deactivate).  
- **CAMPAIGN_MANAGER / ANALYTICS / VIEWER** — org members; created via invite and accept-invite.

API returns roles in **lowercase** for the frontend (`super_admin`, `admin`, `campaign_manager`, `analyst`, `client`); `analyst` = ANALYTICS, `client` = VIEWER.
