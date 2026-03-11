# Auth System — Implementation Report

## What Is Done

### 1. **Register**
- **Route:** `POST /api/v1/auth/register`
- **Body:** `{ "first_name", "last_name", "email", "password", "role?", "language?" }`
- **Response:** `{ "access_token", "refresh_token", "token_type", "expires_in" }`
- **Status:** Implemented. Creates user in MongoDB, returns JWT tokens.

### 2. **Login**
- **Route:** `POST /api/v1/auth/login`
- **Body:** `{ "email", "password" }`
- **Response:** Same as register (tokens).
- **Status:** Implemented.

### 3. **Get profile**
- **Route:** `GET /api/v1/auth/me`
- **Headers:** `Authorization: Bearer <access_token>`
- **Response:** User profile (id, first_name, last_name, email, role, profile_picture, language, timezone, email_verified, is_active, organization_ids, created_at, last_login_at).
- **Status:** Implemented.

### 4. **Delete profile**
- **Route:** `DELETE /api/v1/auth/me`
- **Headers:** `Authorization: Bearer <access_token>`
- **Response:** `{ "message": "Account deleted" }`
- **Status:** Implemented. Removes user document from MongoDB.

### 5. **Patch profile**
- **Route:** `PATCH /api/v1/auth/me`
- **Headers:** `Authorization: Bearer <access_token>`
- **Body (all optional):** `{ "first_name?", "last_name?", "profile_picture?", "language?", "timezone?" }`
- **Response:** Updated user profile.
- **Status:** Implemented.

### 6. **Change password**
- **Route:** `POST /api/v1/auth/me/change-password`
- **Headers:** `Authorization: Bearer <access_token>`
- **Body:** `{ "current_password", "new_password" }`
- **Response:** `{ "message": "Password updated" }`
- **Status:** Implemented.

### 7. **OAuth (Google)**
- **Start:** `GET /api/v1/auth/oauth/google` — redirects to Google sign-in.
- **Callback:** `GET /api/v1/auth/oauth/google/callback?code=...&redirect=true|false`
  - Exchanges code, creates/links user, returns tokens.
  - If `redirect=true` (default): redirects to `FRONTEND_OAUTH_REDIRECT_URI` with tokens in URL fragment.
  - If `redirect=false`: returns JSON `LoginResponse`.
- **Status:** Implemented.

### 8. **Refresh tokens**
- **Route:** `POST /api/v1/auth/refresh`
- **Body:** `{ "refresh_token": "..." }`
- **Response:** New `access_token` and `refresh_token`.
- **Status:** Implemented.

---

## What Needs to Be Added (Optional / Later)

| Item | Description |
|------|-------------|
| Email verification | Send verification email on register; `email_verified` flag and flow. |
| Forgot password | Reset flow (tokenized link + set new password). |
| Rate limiting | Per-IP or per-user limits on login/register (e.g. Redis). |
| Audit log | Log auth events (login, password change, delete account) for compliance. |
| Organization APIs | Create/list organizations and assign users (schema ready, no routes yet). |
| Role-based guards | Enforce role per endpoint (e.g. only `admin` can delete users). |
| Microsoft OAuth | Same pattern as Google if needed later. |

---

## Required Change for Google OAuth

Your Google Cloud OAuth client has:

- **Redirect URI in console:** `http://localhost:8000/auth/google/callback`

The backend uses:

- **Redirect URI:** `http://localhost:8000/api/v1/auth/oauth/google/callback`

**Action:** In [Google Cloud Console](https://console.cloud.google.com/apis/credentials) → your OAuth 2.0 Client → **Authorized redirect URIs**, add:

```text
http://localhost:8000/api/v1/auth/oauth/google/callback
```

You can keep the existing URI or remove it; the one above must be present for Google login to work.

---

## How to Run (Local)

### 1. Python environment

```bash
cd D:\BAAREZ\glimmorareachbackend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. MongoDB

- Install and start MongoDB locally, or use Docker:
  ```bash
  docker run -d -p 27017:27017 --name mongo mongo:7
  ```
- Default connection: `mongodb://localhost:27017` (set in `.env`).

### 3. Environment

- `.env` is already set with local values and your Google OAuth credentials.
- Ensure `GOOGLE_REDIRECT_URI` is exactly:
  `http://localhost:8000/api/v1/auth/oauth/google/callback`
  and that this URI is added in Google Console as above.

### 4. Start the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

### 5. Quick test

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register -H "Content-Type: application/json" -d "{\"first_name\":\"Test\",\"last_name\":\"User\",\"email\":\"test@example.com\",\"password\":\"password123\"}"

# Login
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"password\":\"password123\"}"

# Get profile (use access_token from login response)
curl http://localhost:8000/api/v1/auth/me -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Google login: open in browser:

```text
http://localhost:8000/api/v1/auth/oauth/google
```

After signing in with Google you’ll be redirected to the callback; with default `redirect=true` you’ll be sent to `FRONTEND_OAUTH_REDIRECT_URI` with tokens in the URL hash.
