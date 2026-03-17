# Implementation Plan: Auth & Organization (per backend-api-spec.md)

This plan extends the **existing** auth and codebase to match `backend-api-spec.md` **without breaking** current behavior. New data and routes are added; existing register/login/profile/OAuth stay as-is.

---

## 1. Current State vs Spec

| Area | Current | Spec | Action |
|------|---------|------|--------|
| **User ID** | ObjectId (str in API) | UUID string | Keep ObjectId; expose as `id` in API (no change). New entities (org, invite) use UUID. |
| **User roles** | SUPER_ADMIN, ADMIN, CAMPAIGN_MANAGER, ANALYST, CLIENT | SUPER_ADMIN, ADMIN, CAMPAIGN_MANAGER, ANALYTICS, VIEWER | Add ANALYTICS/VIEWER; map ANALYST→ANALYTICS, CLIENT→VIEWER in DB; in responses return analyst/client (spec Section 10). |
| **User org** | `organization_ids` (list) | `organization_id` (single, null for SUPER_ADMIN) | **Add** `organization_id` (optional str). Keep `organization_ids` for backward compat; API uses `organization_id` / `orgId`. |
| **Password field** | `hashed_password` | `password_hash` | Keep `hashed_password` in DB (no rename). Never return in API. |
| **Avatar** | `profile_picture` | `avatar` | Keep `profile_picture` in DB; **map to `avatar`** in API responses only. |
| **Auth routes** | /api/v1/auth/register, login, refresh, me, PATCH me, DELETE me, change-password, OAuth | login, logout, me, PUT profile, change-password, accept-invite | **Keep** all existing routes. **Add** logout (optional), **add** accept-invite. Align response shapes (name, orgId, createdAt) for me/profile/login. |
| **Organizations** | Stub model only | Full CRUD + collection | **Add** organizations collection, repo, service, routes. |
| **Invitations** | None | Full flow + collection | **Add** invitations collection, repo, service, invite + accept-invite. |
| **User management** | None | create-admin, invite, list, update role, deactivate | **Add** users API (create-admin, invite, list, put role, soft delete). |
| **JWT payload** | sub, type, email (optional) | sub, email, role (uppercase), org_id, exp, iat | **Extend** JWT to include role and org_id; keep existing decode logic. |
| **RBAC** | get_current_user only | require_roles + org scoping | **Add** require_roles dependency; scope ADMIN to own org. |
| **Seed** | None | seed.py for SUPER_ADMIN | **Add** seed.py. |

---

## 2. Data Model Changes (Additive Only)

### 2.1 Users (existing collection)

- **Keep:** first_name, last_name, email, hashed_password, role, profile_picture, language, timezone, email_verified, is_active, organization_ids, oauth_providers, created_at, updated_at, last_login_at.
- **Add (optional):** `organization_id` — single UUID or null. Used by spec; if present, API returns it as `orgId`. If missing, derive from `organization_ids[0]` for backward compat.
- **Role values in DB:** Store uppercase: SUPER_ADMIN, ADMIN, CAMPAIGN_MANAGER, ANALYTICS, VIEWER. Map existing ANALYST→ANALYTICS, CLIENT→VIEWER when reading/writing if needed.
- **No removal:** Keep register and OAuth flows; they can set role and organization_id as needed (e.g. invite flow sets organization_id).

### 2.2 Organizations (new collection)

- **_id:** UUID string (generated with uuid.uuid4().hex or similar).
- **Fields:** name, created_by (user id), is_active (default true), created_at, updated_at.
- **Index:** unique on _id (default).

### 2.3 Invitations (new collection)

- **_id:** UUID string.
- **Fields:** email, role (enum: ADMIN, CAMPAIGN_MANAGER, ANALYTICS, VIEWER), organization_id (UUID), invited_by (user id), token (secrets.token_urlsafe(32)), status (PENDING | ACCEPTED | EXPIRED), expires_at (created_at + 72h), created_at.
- **Index:** unique on token.

---

## 3. API Shape Alignment (No Breaking Change)

- **Login/me/profile responses:** Add/align:
  - `name` = first_name + " " + last_name.
  - `orgId` = organization_id or organization_ids[0] if present, else null.
  - `avatar` = profile_picture.
  - `createdAt` = created_at (ISO 8601).
  - `role` = lowercase for frontend (super_admin, admin, campaign_manager, analyst, client); map ANALYTICS→analyst, VIEWER→client.
- **Existing fields** (id, email, etc.) remain; only add/rename for spec compatibility in the same response.

---

## 4. Implementation Phases

### Phase 1: Foundation (models, DB, config)

1. **Roles:** Extend UserRole (or add internal enum) for ANALYTICS and VIEWER; keep backward mapping from existing ANALYST/CLIENT.
2. **User model:** Add optional `organization_id`; ensure role stored uppercase in DB; add helper to get “response role” (lowercase, analyst/client).
3. **Organization model:** Full document model and Pydantic schemas (create, update, response).
4. **Invitation model:** Full document model and Pydantic schemas.
5. **Config:** Add from spec: JWT_EXPIRE_MINUTES (or keep current name), SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD, SMTP_*, INVITE_BASE_URL, DB_NAME if different from current.
6. **Repositories:** OrganizationRepository (CRUD); InvitationRepository (create, get by token, update status, list by org). UserRepository: add methods for list by organization_id, update role, set is_active=False; support organization_id in create/update.

### Phase 2: Auth alignment

1. **JWT:** Include role (uppercase) and org_id in payload; keep sub, email, exp, iat; keep existing access/refresh behavior.
2. **Login response:** Return access_token, token_type, and **user** object (id, name, email, role lowercase, orgId, avatar, createdAt) — align with spec; keep existing token fields.
3. **GET /auth/me:** Return same user shape (name, orgId, avatar, createdAt, role lowercase).
4. **PUT /auth/profile:** Accept first_name, last_name, language, avatar; return updated user in same shape. (Keep existing PATCH /auth/me if needed; can alias or merge.)
5. **POST /auth/accept-invite:** Body: token, first_name, last_name, password. Validate token (PENDING, not expired), create user with invitation’s role and organization_id, mark invite ACCEPTED, return login-style response (token + user).
6. **POST /auth/logout:** Optional; 200 + message (client clears token); no server-side blocklist in this phase.

### Phase 3: Organizations API

1. **POST /organizations:** Require SUPER_ADMIN; body: name; create org, return id, name, created_by, is_active, created_at.
2. **GET /organizations:** Require SUPER_ADMIN; return list with id, name, is_active, created_at, member_count (optional).
3. **GET /organizations/:id:** SUPER_ADMIN (any org) or ADMIN (own org only); return one org.
4. **PUT /organizations/:id:** SUPER_ADMIN or ADMIN (own org); body: name, is_active; return updated org.

### Phase 4: User management API

1. **POST /users/create-admin:** Require SUPER_ADMIN; body: first_name, last_name, email, password, organization_id; create user with role ADMIN and organization_id; return user (no password).
2. **POST /users/invite:** Require ADMIN; body: email, role (CAMPAIGN_MANAGER, ANALYTICS, VIEWER); create invitation, (optional) send email; return invitation (id, email, role, status PENDING, expires_at).
3. **GET /users:** SUPER_ADMIN (all users or by org) or ADMIN (users in own org only); return list (id, name, email, role, is_active, created_at).
4. **PUT /users/:id/role:** ADMIN only; body: role; ensure target user in same org; update role; return updated user.
5. **DELETE /users/:id:** ADMIN only; soft delete (set is_active=false); return success.

### Phase 5: RBAC and security

1. **require_roles dependency:** From JWT get user id; load user from DB; check is_active; check user.role in allowed_roles; return user; 401 if no/invalid token, 403 if wrong role.
2. **Org scoping:** For ADMIN: on GET/ PUT organizations/:id and users list/role/delete, verify resource.organization_id == current_user.organization_id (or equivalent).
3. **Optional:** Rate limit POST /auth/login (e.g. 10 per IP per 15 min → 429).

### Phase 6: Seed and invite email

1. **seed.py:** If no user with role SUPER_ADMIN exists, create one from SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASSWORD (hashed); organization_id null.
2. **Invite email (optional):** On POST /users/invite, send email with link INVITE_BASE_URL/register?token=... using SMTP config; if SMTP not set, skip or log.

---

## 5. File and Route Layout (Additive)

- **Keep:** app/api/v1/auth.py (existing routes), app/core/security.py, app/core/deps.py (get_current_user, etc.), app/services/auth.py, app/repositories/user.py, app/models/user.py (extend only).
- **Add:**
  - app/models/invitation.py
  - app/schemas/organization.py, app/schemas/user.py (for create-admin, invite, list, role update)
  - app/repositories/organization.py, app/repositories/invitation.py
  - app/services/org_service.py, app/services/user_service.py (invite, create-admin logic)
  - app/api/v1/organizations.py, app/api/v1/users.py
  - app/core/dependencies.py (or extend deps.py): require_roles(allowed_roles), get_current_user_optional
  - seed.py (project root)
- **Routers:** Register organizations and users under api_router (e.g. prefix /organizations, /users); keep /auth as is. Base path can stay /api/v1.

---

## 6. Backward Compatibility Checklist

- [ ] Existing POST /auth/register still works (can remain for backward compat or restricted later).
- [ ] Existing POST /auth/login returns tokens; add `user` object in response without removing existing fields.
- [ ] GET /auth/me and PATCH /auth/me keep working; response shape extended (name, orgId, avatar, createdAt).
- [ ] Change-password and delete profile unchanged.
- [ ] Google OAuth unchanged.
- [ ] Existing users without organization_id still readable; orgId in response can be null or from organization_ids.
- [ ] JWT decode still works; new payload fields (role, org_id) optional when reading.

---

## 7. Order of Implementation (Recommended)

1. **Phase 1** — Models, schemas, repos, config (organizations, invitations, user extensions).
2. **Phase 2** — Auth alignment (JWT payload, login/me/profile response shape, accept-invite).
3. **Phase 5 (partial)** — require_roles and get_current_user returning full user with role/org_id so Phase 3/4 can use it.
4. **Phase 3** — Organizations CRUD.
5. **Phase 4** — User management (create-admin, invite, list, role, soft delete).
6. **Phase 5 (rest)** — Org scoping and optional rate limit.
7. **Phase 6** — seed.py and optional invite email.

---

## 8. Summary

- **Existing auth and user data stay;** only additive fields and new endpoints.
- **New:** organizations + invitations collections, their APIs, user management APIs, JWT/response alignment, RBAC with require_roles and org scoping, seed script, optional invite email.
- **Spec alignment:** Role names (ANALYTICS/VIEWER + analyst/client), orgId, name, avatar, createdAt, JWT structure, and RBAC matrix as reference for future permission checks.

Once you approve this plan, we can start with **Phase 1** (models, schemas, repos, config) and then proceed phase by phase.
