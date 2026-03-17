# Glimmora Reach — Backend API Specification
## Auth & Organization System
**Stack: Python 3.11+ · FastAPI · MongoDB (Motor async) · PyJWT · bcrypt / passlib · Pydantic v2**

---

## 1. Tech Stack Requirements

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Database | MongoDB |
| DB Driver | Motor (async MongoDB driver for Python) |
| Auth Tokens | PyJWT |
| Password Hashing | passlib with bcrypt backend |
| Request Validation | Pydantic v2 |
| Environment Config | python-dotenv |
| Email (invitations) | fastapi-mail or SMTP via Python smtplib |

---

## 2. Project Folder Structure

```
backend/
│
├── app/
│   ├── api/
│   │   ├── auth.py             ← login, logout, me, profile, accept-invite
│   │   ├── organizations.py    ← CRUD for organizations
│   │   └── users.py            ← invite, list, update role, deactivate
│   │
│   ├── core/
│   │   ├── config.py           ← reads .env variables
│   │   ├── security.py         ← JWT create/decode, password hash/verify
│   │   └── dependencies.py     ← FastAPI dependencies: get_current_user, require_roles
│   │
│   ├── models/
│   │   ├── user.py             ← MongoDB document model for users collection
│   │   ├── organization.py     ← MongoDB document model for organizations collection
│   │   └── invitation.py       ← MongoDB document model for invitations collection
│   │
│   ├── schemas/
│   │   ├── auth.py             ← Pydantic request/response schemas for auth routes
│   │   ├── organization.py     ← Pydantic schemas for org routes
│   │   └── user.py             ← Pydantic schemas for user routes
│   │
│   ├── services/
│   │   ├── auth_service.py     ← business logic: login, token generation, invite acceptance
│   │   ├── org_service.py      ← business logic: create/update org
│   │   └── user_service.py     ← business logic: invite user, update role, deactivate
│   │
│   └── db/
│       └── mongodb.py          ← Motor client setup, database connection helper
│
├── seed.py                     ← Script to create the initial Super Admin user in DB
├── main.py                     ← FastAPI app entry point, router registration, CORS setup
├── .env                        ← Environment variables (never commit to git)
└── requirements.txt
```

---

## 3. MongoDB Collections

### 3.1 users

| Field | Type | Notes |
|---|---|---|
| _id | UUID string | Primary key |
| first_name | string | Required |
| last_name | string | Required |
| email | string | Unique, required, lowercase |
| password_hash | string | bcrypt hash, never returned in responses |
| role | string (enum) | SUPER_ADMIN, ADMIN, CAMPAIGN_MANAGER, ANALYTICS, VIEWER |
| organization_id | UUID string or null | null for SUPER_ADMIN only |
| is_active | boolean | Default true |
| language | string | Default "en" |
| avatar | string or null | URL to avatar image, optional |
| created_at | datetime (UTC) | Set on insert |
| updated_at | datetime (UTC) | Updated on every write |

Index: unique on email field.

---

### 3.2 organizations

| Field | Type | Notes |
|---|---|---|
| _id | UUID string | Primary key |
| name | string | Required |
| created_by | UUID string | References the SUPER_ADMIN user id who created it |
| is_active | boolean | Default true |
| created_at | datetime (UTC) | Set on insert |
| updated_at | datetime (UTC) | Updated on every write |

---

### 3.3 invitations

| Field | Type | Notes |
|---|---|---|
| _id | UUID string | Primary key |
| email | string | The email address being invited |
| role | string (enum) | ADMIN, CAMPAIGN_MANAGER, ANALYTICS, VIEWER (not SUPER_ADMIN) |
| organization_id | UUID string | Which org this invite belongs to |
| invited_by | UUID string | User id of the ADMIN who sent the invite |
| token | string | Secure random token (use secrets.token_urlsafe) |
| status | string (enum) | PENDING, ACCEPTED, EXPIRED |
| expires_at | datetime (UTC) | Set to 72 hours after creation |
| created_at | datetime (UTC) | Set on insert |

Index: unique on token field.

---

## 4. Role Definitions

There are 5 roles in the system. Roles are stored as uppercase strings in MongoDB.

**SUPER_ADMIN**
- Global role, not tied to any organization
- organization_id is null for this role
- Created only via the seed script — no API registration
- Can create organizations and create ADMIN users for each org
- Can view all organizations and all users across the platform

**ADMIN**
- Belongs to exactly one organization
- Created by SUPER_ADMIN via the create-admin API
- Can invite and manage users within their own organization
- Can manage organization settings
- Cannot access other organizations

**CAMPAIGN_MANAGER**
- Belongs to exactly one organization
- Invited by an ADMIN
- Can create, edit, and manage campaigns (to be enforced in future ads APIs)
- Cannot manage team members or org settings

**ANALYTICS**
- Belongs to exactly one organization
- Invited by an ADMIN
- Read-only access to analytics and reports
- Cannot create or edit campaigns

**VIEWER**
- Belongs to exactly one organization
- Invited by an ADMIN
- Most restricted role — view-only access to dashboards
- Cannot export data or manage anything

---

## 5. Auth Flows (Step by Step)

### 5.1 Super Admin Seeding (one-time setup)

1. Developer runs seed.py manually on the server
2. Script checks if a SUPER_ADMIN already exists in the users collection
3. If not, creates a user document with role SUPER_ADMIN and no organization_id
4. Password is provided as an environment variable in .env and hashed before storing
5. Super Admin logs in through the normal login endpoint

---

### 5.2 Organization Creation Flow

1. SUPER_ADMIN sends a POST to /organizations with organization name
2. System creates a new organization document in MongoDB
3. System returns the new organization id and details
4. SUPER_ADMIN then sends a POST to /users/create-admin with email, name, password, and the organization_id
5. System creates a new user with role ADMIN linked to that organization
6. SUPER_ADMIN shares the credentials with the new Admin securely

---

### 5.3 Admin Login Flow

1. Admin receives credentials from SUPER_ADMIN
2. Admin sends email and password to POST /auth/login
3. System verifies password hash
4. System returns a JWT token and the full user object
5. Admin stores the token and is redirected to the dashboard

---

### 5.4 User Invite Flow

1. ADMIN sends POST /users/invite with email and desired role
2. System creates an invitation document with status PENDING and generates a secure random token
3. System sends an email with the invite link (containing the token)
4. Invited user clicks the link, opens the accept-invite page on the frontend
5. User submits their name and chosen password to POST /auth/accept-invite with the token
6. System validates the token is PENDING and not expired
7. System creates the user account linked to the organization from the invitation
8. System marks the invitation as ACCEPTED
9. User is logged in automatically — system returns a JWT token

---

### 5.5 Standard Login Flow

1. User submits email and password to POST /auth/login
2. System looks up user by email
3. System checks is_active is true
4. System verifies the submitted password against the stored bcrypt hash
5. If valid, system generates a JWT with the payload described in Section 7
6. System returns the JWT and the user object as described in Section 8
7. Frontend stores the token and user in localStorage

---

## 6. API Endpoints

### 6.1 Auth Endpoints

| Method | Path | Auth Required | Allowed Roles | Purpose |
|---|---|---|---|---|
| POST | /auth/login | No | Any | Login with email and password |
| POST | /auth/logout | Yes (JWT) | Any | Invalidate token (client-side clear) |
| GET | /auth/me | Yes (JWT) | Any | Get current user profile |
| PUT | /auth/profile | Yes (JWT) | Any | Update own name, language, avatar |
| POST | /auth/change-password | Yes (JWT) | Any | Change own password |
| POST | /auth/accept-invite | No | — | Complete registration from invite token |

---

### 6.2 Organization Endpoints

| Method | Path | Auth Required | Allowed Roles | Purpose |
|---|---|---|---|---|
| POST | /organizations | Yes (JWT) | SUPER_ADMIN | Create a new organization |
| GET | /organizations | Yes (JWT) | SUPER_ADMIN | List all organizations |
| GET | /organizations/:id | Yes (JWT) | SUPER_ADMIN, ADMIN | Get one organization's details |
| PUT | /organizations/:id | Yes (JWT) | SUPER_ADMIN, ADMIN | Update organization name or status |

Note: ADMIN can only access and update their own organization. SUPER_ADMIN can access any.

---

### 6.3 User Management Endpoints

| Method | Path | Auth Required | Allowed Roles | Purpose |
|---|---|---|---|---|
| POST | /users/create-admin | Yes (JWT) | SUPER_ADMIN | Create an ADMIN user for an org |
| POST | /users/invite | Yes (JWT) | ADMIN | Send an invite to a new user |
| GET | /users | Yes (JWT) | SUPER_ADMIN, ADMIN | List users (scoped to org for ADMIN) |
| PUT | /users/:id/role | Yes (JWT) | ADMIN | Change a user's role within the org |
| DELETE | /users/:id | Yes (JWT) | ADMIN | Deactivate (soft delete) a user |

---

## 7. Request and Response Fields

### POST /auth/login

Request fields:
- email — string, required
- password — string, required

Response fields:
- access_token — the JWT string
- token_type — always "bearer"
- user — object containing: id, name, email, role (lowercase), orgId, avatar, createdAt

---

### GET /auth/me

No request body.

Response fields:
- id — user uuid
- name — full name (first_name + last_name joined)
- email
- role — lowercase string (super_admin, admin, campaign_manager, analyst, viewer)
- orgId — organization uuid or null
- avatar — url or null
- createdAt — ISO 8601 datetime string

---

### PUT /auth/profile

Request fields (all optional):
- first_name
- last_name
- language
- avatar

Response: updated user object (same shape as /auth/me)

---

### POST /auth/change-password

Request fields:
- current_password — string, required
- new_password — string, required (minimum 8 characters)

Response: success message

---

### POST /auth/accept-invite

Request fields:
- token — the invite token from the link, required
- first_name — required
- last_name — required
- password — required (minimum 8 characters)

Response: same as login response (access_token + user object, user is logged in automatically)

---

### POST /organizations

Request fields:
- name — string, required

Response fields:
- id
- name
- created_by
- is_active
- created_at

---

### GET /organizations

No request body.

Response: array of organization objects, each with id, name, is_active, created_at, member_count

---

### GET /organizations/:id

No request body.

Response: single organization object with id, name, is_active, created_at, updated_at

---

### PUT /organizations/:id

Request fields (all optional):
- name
- is_active

Response: updated organization object

---

### POST /users/create-admin

Request fields:
- first_name — required
- last_name — required
- email — required
- password — required
- organization_id — required (must be a valid existing org id)

Response: created user object (no password_hash)

---

### POST /users/invite

Request fields:
- email — required
- role — required (CAMPAIGN_MANAGER, ANALYTICS, or VIEWER only — not ADMIN or SUPER_ADMIN)

Response fields:
- id — invitation id
- email
- role
- status — PENDING
- expires_at

---

### GET /users

No request body.

Response: array of user objects within the caller's organization (ADMIN sees own org, SUPER_ADMIN sees all)

Each user object: id, name, email, role, is_active, created_at

---

### PUT /users/:id/role

Request fields:
- role — required (new role to assign)

Response: updated user object

Note: ADMIN cannot assign SUPER_ADMIN role. ADMIN can only change roles within their own organization.

---

### DELETE /users/:id

No request body.

Response: success message

Note: This is a soft delete — sets is_active to false. The user record is kept in the database.

---

## 8. JWT Token Structure

The JWT payload must contain the following fields:

- sub — the user's id (UUID string)
- email — the user's email
- role — the user's role in uppercase (SUPER_ADMIN, ADMIN, etc.)
- org_id — the user's organization_id (UUID string or null)
- exp — expiry timestamp (Unix seconds)
- iat — issued-at timestamp (Unix seconds)

JWT signing algorithm: HS256
JWT secret: loaded from environment variable JWT_SECRET

---

## 9. Login Response Shape (Frontend Alignment)

The frontend auth-context.tsx reads the user object from the login response and stores it in localStorage.

The user object in the login response must use these exact field names to match the frontend User type:

- id — UUID string
- name — first_name and last_name joined with a space
- email — string
- role — **lowercase** string: super_admin, admin, campaign_manager, analyst, viewer
  - Note: Store role in uppercase in MongoDB, but return it lowercase in all API responses
  - Frontend role "analyst" maps to backend role "ANALYTICS" — convert in both directions
  - Frontend role "client" maps to backend role "VIEWER" — convert in both directions
- orgId — UUID string or null (note: camelCase to match frontend, not organization_id)
- avatar — URL string or null
- createdAt — ISO 8601 string

The full login response shape:
```
{
  access_token: "...",
  token_type: "bearer",
  user: {
    id: "...",
    name: "First Last",
    email: "...",
    role: "admin",
    orgId: "...",
    avatar: null,
    createdAt: "2025-01-01T00:00:00Z"
  }
}
```

---

## 10. Role Name Mapping Table

Backend stores roles in uppercase. Frontend uses lowercase with different names for two roles.

| Backend (MongoDB) | API Response (to frontend) | Frontend Role value |
|---|---|---|
| SUPER_ADMIN | super_admin | super_admin |
| ADMIN | admin | admin |
| CAMPAIGN_MANAGER | campaign_manager | campaign_manager |
| ANALYTICS | analyst | analyst |
| VIEWER | client | client |

The services layer must handle this mapping when constructing user objects for responses.

---

## 11. RBAC Permission Matrix

This matches the frontend permissions.ts file. Use this as reference for role-based middleware.

| Permission | SUPER_ADMIN | ADMIN | CAMPAIGN_MANAGER | ANALYTICS | VIEWER |
|---|---|---|---|---|---|
| campaign:view | Yes | Yes | Yes | Yes | Yes |
| campaign:create | Yes | Yes | Yes | No | No |
| campaign:edit | Yes | Yes | Yes | No | No |
| campaign:delete | Yes | Yes | No | No | No |
| analytics:view | Yes | Yes | Yes | Yes | Yes |
| analytics:export | Yes | Yes | No | Yes | No |
| creatives:view | Yes | Yes | Yes | Yes | Yes |
| creatives:manage | Yes | Yes | Yes | No | No |
| targeting:view | Yes | Yes | Yes | No | No |
| targeting:manage | Yes | Yes | Yes | No | No |
| placements:view | Yes | Yes | Yes | Yes | No |
| placements:manage | Yes | Yes | No | No | No |
| automation:view | Yes | Yes | Yes | No | No |
| automation:manage | Yes | Yes | No | No | No |
| ai:view | Yes | Yes | Yes | No | No |
| settings:org | No | Yes | No | No | No |
| settings:team | No | Yes | No | No | No |
| settings:roles | No | Yes | No | No | No |
| settings:dsp | No | Yes | No | No | No |
| settings:crm | No | Yes | No | No | No |
| settings:webhooks | No | Yes | No | No | No |
| platform:orgs | Yes | No | No | No | No |
| platform:billing | Yes | No | No | No | No |
| platform:settings | Yes | No | No | No | No |
| platform:audit | Yes | No | No | No | No |

---

## 12. RBAC Middleware Rules

Implement a FastAPI dependency called require_roles that:

1. Reads the Authorization header from the request (format: "Bearer <token>")
2. Decodes and validates the JWT
3. Looks up the user in MongoDB by the id in the JWT sub field
4. Checks that is_active is true
5. Checks that the user's role is in the list of allowed roles for that endpoint
6. Rejects with HTTP 401 if no valid token
7. Rejects with HTTP 403 if valid token but wrong role
8. Returns the current user object to the route handler

Additionally enforce organization scoping:
- ADMIN endpoints that operate on users must verify that the target user belongs to the same organization as the ADMIN making the request
- SUPER_ADMIN has no such restriction

---

## 13. Security Requirements

**Password hashing**
- Use bcrypt with a work factor (rounds) of at least 12
- Never store plain text passwords
- Never return password_hash in any API response

**JWT security**
- Access token expiry: 60 minutes (configurable via env)
- Use a strong random secret of at least 32 characters for JWT_SECRET
- Algorithm: HS256

**Rate limiting**
- Apply rate limiting on POST /auth/login
- Limit to 10 attempts per IP per 15-minute window
- Return HTTP 429 Too Many Requests when exceeded

**Input validation**
- All request fields validated via Pydantic
- Email addresses normalized to lowercase before storing
- Passwords must be at least 8 characters

**CORS**
- Only allow origins listed in CORS_ORIGINS environment variable
- In development: allow http://localhost:3000
- In production: allow only the deployed frontend domain

**Invite token security**
- Generate tokens using Python's secrets.token_urlsafe with at least 32 bytes
- Tokens expire after 72 hours
- A token can only be used once — mark as ACCEPTED immediately on use

---

## 14. Environment Variables

Create a .env file in the project root with these variables. Do not commit this file to git.

| Variable | Description |
|---|---|
| MONGODB_URL | Full MongoDB connection string |
| DB_NAME | MongoDB database name (e.g. glimmora_reach) |
| JWT_SECRET | Secret key for signing JWTs — use a long random string |
| JWT_EXPIRE_MINUTES | Access token expiry in minutes (recommended: 60) |
| SUPER_ADMIN_EMAIL | Email for the seeded Super Admin account |
| SUPER_ADMIN_PASSWORD | Password for the seeded Super Admin account |
| CORS_ORIGINS | Comma-separated list of allowed frontend origins |
| SMTP_HOST | SMTP server host for sending invite emails |
| SMTP_PORT | SMTP server port |
| SMTP_USER | SMTP username |
| SMTP_PASSWORD | SMTP password |
| FROM_EMAIL | The from address for outgoing emails |
| INVITE_BASE_URL | Base URL of the frontend for building invite links (e.g. https://app.glimmora.io) |

---

## 15. Frontend Integration Notes

Once the backend is live, these changes are needed on the frontend:

**auth-context.tsx**
- Replace the mock login function (which picks from DUMMY_ROLE_USERS) with a real fetch call to POST /auth/login
- On successful login, store the returned access_token in localStorage under key glimmora_token
- Store the returned user object in localStorage under key glimmora_user (same key already in use)
- On app load, call GET /auth/me using the stored token to verify the session is still valid
- If /auth/me returns 401, clear storage and redirect to /login

**Token storage**
- Store the JWT in localStorage key: glimmora_token
- Send it on all authenticated requests as: Authorization: Bearer <token>

**Role name alignment**
- The frontend Role type uses: super_admin, admin, campaign_manager, analyst, client
- The backend returns: super_admin, admin, campaign_manager, analyst, client (already matched per Section 10)
- No transformation needed on the frontend side

**Field name alignment**
- Backend returns orgId (camelCase) — matches the frontend User type directly
- Backend returns name as a single joined string — matches the frontend User type directly
- Backend returns createdAt in ISO 8601 format — matches the frontend User type directly

**Register page**
- The current register page creates a local admin user — replace with POST /auth/accept-invite
- The accept-invite page receives the token from the URL query parameter: /register?token=xxxxx

**API base URL**
- Add environment variable NEXT_PUBLIC_API_URL to the frontend .env.local
- All fetch calls should prefix with this base URL
