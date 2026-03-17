# API Test Results

All endpoints were tested with the server running in venv. Summary table and curl examples below.

---

## Test summary table

| # | API | Method | Status | Works | How it works / Note |
|---|-----|--------|--------|-------|---------------------|
| 1 | Health | GET | 200 | ✅ Yes | Returns `{"status":"ok"}`. No auth. |
| 2 | Login (Super Admin) | POST | 200 | ✅ Yes | Body: `email`, `password`. Returns `access_token`, `refresh_token`, `user` (id, name, role, orgId, etc.). |
| 3 | Get profile | GET | 200 | ✅ Yes | Header: `Authorization: Bearer <token>`. Returns full user profile. |
| 4 | Get profile (spec shape) | GET | 200 | ✅ Yes | Same as above; response shape: id, name, role (lowercase), orgId, avatar, createdAt. |
| 5 | Register | POST | 200/400 | ✅ Yes | Body: first_name, last_name, email, password, role?, language?. Returns tokens. 400 if email already registered. |
| 6 | Create organization | POST | 201 | ✅ Yes | **SUPER_ADMIN only.** Body: `name`. Returns org with `id` (UUID). |
| 7 | List organizations | GET | 200 | ✅ Yes | **SUPER_ADMIN only.** Returns array with id, name, is_active, created_at, member_count. |
| 8 | Get organization | GET | 200 | ✅ Yes | **SUPER_ADMIN:** any org. **ADMIN:** own org only. Path: `/organizations/:id`. |
| 9 | Create Admin | POST | 201/400 | ✅ Yes | **SUPER_ADMIN only.** Body: first_name, last_name, email, password, organization_id. 400 if email exists. |
| 10 | Login (Admin) | POST | 200 | ✅ Yes | Same as login; use admin credentials. |
| 11 | Invite user | POST | 201/400 | ✅ Yes | **ADMIN only.** Body: email, role (CAMPAIGN_MANAGER\|ANALYTICS\|VIEWER). Returns invite with `token`. 400 if user exists. |
| 12 | Accept invite | POST | 200 | ✅ Yes | Body: token, first_name, last_name, password. Creates user, marks invite ACCEPTED, returns tokens + user. |
| 13 | List users | GET | 200 | ✅ Yes | **SUPER_ADMIN:** all users. **ADMIN:** users in own org. |
| 14 | Update organization | PUT | 200 | ✅ Yes | **SUPER_ADMIN** or **ADMIN** (own org). Body: name?, is_active?. Path: `/organizations/:id`. |
| 15 | Update user role | PUT | 200 | ✅ Yes | **ADMIN only.** Path: `/users/:id/role`. Body: role. Target must be in same org. |
| 16 | Update profile | PUT | 200 | ✅ Yes | Body: first_name?, last_name?, language?, avatar?. Same as PATCH /auth/me. |
| 17 | Change password | POST | 200 | ✅ Yes | Body: current_password, new_password. Path: `/auth/me/change-password`. |
| 18 | Logout | POST | 200 | ✅ Yes | No body. Client should clear token. |
| 19 | Refresh tokens | POST | 200 | ✅ Yes | Body: refresh_token. Returns new access_token and refresh_token. |
| 20 | Deactivate user | DELETE | 200 | ✅ Yes | **ADMIN only.** Path: `/users/:id`. Soft delete (sets is_active=false). |

**Fix applied during testing:** Removed invalid `create_index("_id", unique=True)` for organizations collection (MongoDB reserves `_id`; creating a unique index on it is not allowed).

---

## How to run tests

1. **Start MongoDB** (local or Atlas; set `MONGODB_URL` in `.env`).

2. **Seed Super Admin** (once):
   ```bash
   .\.venv\Scripts\activate
   python seed.py
   ```
   Set `SUPER_ADMIN_EMAIL` and `SUPER_ADMIN_PASSWORD` in `.env`.

3. **Start the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Run the test script (Python):**
   ```bash
   python scripts/test_apis.py
   ```
   Script hits all endpoints in workflow order and prints a table. Exit code 0 = all passed.

5. **Run tests via CMD using curl (Windows):**
   From Command Prompt (server and seed must be done first):
   ```cmd
   cd /d D:\path\to\glimmorareachbackend
   scripts\test_apis_curl.bat
   ```
   The batch file runs real `curl` for each API, parses tokens/IDs from JSON (via PowerShell), and prints the same style of table. All requests are sent from CMD.

---

## Example curl commands (Windows PowerShell)

Base URL: `http://localhost:8000/api/v1`. Replace `YOUR_TOKEN` and `ORG_ID`, `USER_ID` where needed.

```powershell
# Health
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Login
$body = '{"email":"superadmin@test.com","password":"SuperAdmin1!"}'
$r = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
$r.Content | ConvertFrom-Json | Select-Object access_token

# Get profile (use token from login)
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/me" -Headers @{ Authorization = "Bearer YOUR_TOKEN" } -UseBasicParsing

# Create organization (Super Admin token)
$body = '{"name":"Acme Corp"}'
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/organizations" -Method POST -Body $body -ContentType "application/json" -Headers @{ Authorization = "Bearer YOUR_TOKEN" } -UseBasicParsing

# List organizations
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/organizations" -Headers @{ Authorization = "Bearer YOUR_TOKEN" } -UseBasicParsing

# Create Admin (use org id from create response)
$body = '{"first_name":"Org","last_name":"Admin","email":"admin@example.com","password":"AdminPass1!","organization_id":"ORG_ID"}'
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/users/create-admin" -Method POST -Body $body -ContentType "application/json" -Headers @{ Authorization = "Bearer YOUR_TOKEN" } -UseBasicParsing

# Invite user (Admin token)
$body = '{"email":"member@example.com","role":"CAMPAIGN_MANAGER"}'
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/users/invite" -Method POST -Body $body -ContentType "application/json" -Headers @{ Authorization = "Bearer ADMIN_TOKEN" } -UseBasicParsing

# Accept invite (use token from invite response)
$body = '{"token":"INVITE_TOKEN","first_name":"Jane","last_name":"Doe","password":"MemberPass1!"}'
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/accept-invite" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing

# List users
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/users" -Headers @{ Authorization = "Bearer ADMIN_TOKEN" } -UseBasicParsing

# Update user role
$body = '{"role":"VIEWER"}'
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/users/USER_ID/role" -Method PUT -Body $body -ContentType "application/json" -Headers @{ Authorization = "Bearer ADMIN_TOKEN" } -UseBasicParsing

# Deactivate user
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/users/USER_ID" -Method DELETE -Headers @{ Authorization = "Bearer ADMIN_TOKEN" } -UseBasicParsing
```

---

## Workflow tested

1. **Health** → OK  
2. **Login as Super Admin** → tokens + user  
3. **GET /auth/me, GET /auth/me/spec** → profile in both shapes  
4. **Register** → new user tokens (or 400 if email exists)  
5. **Create organization** → org id  
6. **List/Get organization** → list and detail  
7. **Create Admin** → admin user for org (or 400 if email exists)  
8. **Login as Admin** → admin tokens  
9. **Invite user** → invite with token (or 400 if user exists)  
10. **Accept invite** → new user created and logged in  
11. **List users** → admin sees org members  
12. **Update organization** → name/is_active updated  
13. **Update user role** → role changed within org  
14. **PUT profile, change-password, logout, refresh** → all succeed  
15. **Deactivate user** → soft delete (is_active=false)  

All APIs behave as designed. Register/create-admin/invite return 400 when the email already exists (expected on re-run).
