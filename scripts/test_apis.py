"""Test all APIs and print a results table. Run: python scripts/test_apis.py (server must be running)."""
import json
import sys
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"
API = f"{BASE}/api/v1"

def req(method, url, body=None, token=None):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.getcode(), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode() if e.fp else ""
    except Exception as e:
        return None, str(e)[:100]

rows = []
token = refresh_token = org_id = admin_token = invite_token = None

# 1. Health
code, body = req("GET", f"{BASE}/health")
rows.append(("GET /health", code, code == 200, body[:60] if body else ""))

# 2. Login Super Admin
code, body = req("POST", f"{API}/auth/login", {"email": "superadmin@test.com", "password": "SuperAdmin1!"})
ok = code == 200
rows.append(("POST /auth/login (Super Admin)", code, ok, "tokens + user" if ok else (body[:60] if body else "")))
if ok and body:
    d = json.loads(body)
    token = d.get("access_token")
    refresh_token = d.get("refresh_token")

# 3. GET /auth/me
code, body = req("GET", f"{API}/auth/me", token=token)
rows.append(("GET /auth/me", code, code == 200, "profile" if code == 200 else (body[:60] if body else "")))

# 4. GET /auth/me/spec
code, body = req("GET", f"{API}/auth/me/spec", token=token)
rows.append(("GET /auth/me/spec", code, code == 200, "id,name,role,orgId" if code == 200 else (body[:60] if body else "")))

# 5. Register
code, body = req("POST", f"{API}/auth/register", {"first_name": "Curler", "last_name": "Test", "email": "curler@test.com", "password": "Password1!"})
ok = code in (200, 201) or (code == 400 and body and "already registered" in body.lower())
rows.append(("POST /auth/register", code, ok, "tokens" if code in (200, 201) else ("already registered" if code == 400 else (body[:60] if body else ""))))

# 6. POST /organizations
code, body = req("POST", f"{API}/organizations", {"name": "Test Org"}, token=token)
ok = code in (200, 201)
rows.append(("POST /organizations", code, ok, "created" if ok else (body[:60] if body else "")))
if ok and body:
    org_id = json.loads(body).get("id")

# 7. GET /organizations
code, body = req("GET", f"{API}/organizations", token=token)
rows.append(("GET /organizations", code, code == 200, "list" if code == 200 else (body[:60] if body else "")))

# 8. GET /organizations/:id
if org_id:
    code, body = req("GET", f"{API}/organizations/{org_id}", token=token)
    rows.append(("GET /organizations/:id", code, code == 200, "org detail" if code == 200 else (body[:60] if body else "")))

# 9. POST /users/create-admin
if org_id:
    code, body = req("POST", f"{API}/users/create-admin", {"first_name": "Org", "last_name": "Admin", "email": "admin@test.com", "password": "AdminPass1!", "organization_id": org_id}, token=token)
    ok = code in (200, 201) or (code == 400 and body and "already registered" in body.lower())
    rows.append(("POST /users/create-admin", code, ok, "admin created" if code in (200, 201) else ("already exists" if code == 400 else (body[:60] if body else ""))))

# 10. Login Admin
code, body = req("POST", f"{API}/auth/login", {"email": "admin@test.com", "password": "AdminPass1!"})
ok = code == 200
rows.append(("POST /auth/login (Admin)", code, ok, "tokens" if ok else (body[:60] if body else "")))
if ok and body:
    admin_token = json.loads(body).get("access_token")

# 11. POST /users/invite
code, body = req("POST", f"{API}/users/invite", {"email": "member@test.com", "role": "CAMPAIGN_MANAGER"}, token=admin_token)
ok = code in (200, 201) or (code == 400 and body and "already exists" in body.lower())
rows.append(("POST /users/invite", code, ok, "invite + token" if code in (200, 201) else ("user exists" if code == 400 else (body[:60] if body else ""))))
if ok and body:
    invite_token = json.loads(body).get("token")

# 12. POST /auth/accept-invite (create member user)
if invite_token:
    code, body = req("POST", f"{API}/auth/accept-invite", {"token": invite_token, "first_name": "Member", "last_name": "User", "password": "MemberPass1!"})
    rows.append(("POST /auth/accept-invite", code, code == 200, "tokens + user" if code == 200 else (body[:60] if body else "")))

# 13. GET /users (now includes member@test.com)
code, body = req("GET", f"{API}/users", token=admin_token)
user_id_for_role = member_user_id = None
if code == 200 and body:
    arr = json.loads(body)
    if arr:
        for u in arr:
            if u.get("email") == "member@test.com":
                member_user_id = u.get("id")
                user_id_for_role = u.get("id")
                break
        if not user_id_for_role and arr:
            user_id_for_role = arr[0].get("id")
rows.append(("GET /users", code, code == 200, "user list" if code == 200 else (body[:60] if body else "")))

# 14. PUT /organizations/:id
if org_id:
    code, body = req("PUT", f"{API}/organizations/{org_id}", {"name": "Test Org Updated", "is_active": True}, token=token)
    rows.append(("PUT /organizations/:id", code, code == 200, "updated" if code == 200 else (body[:60] if body else "")))

# 15. PUT /users/:id/role
if admin_token and user_id_for_role:
    code, body = req("PUT", f"{API}/users/{user_id_for_role}/role", {"role": "VIEWER"}, token=admin_token)
    rows.append(("PUT /users/:id/role", code, code == 200, "role updated" if code == 200 else (body[:60] if body else "")))

# 16. PUT /auth/profile
code, body = req("PUT", f"{API}/auth/profile", {"first_name": "Super", "language": "en"}, token=token)
rows.append(("PUT /auth/profile", code, code == 200, "updated profile" if code == 200 else (body[:60] if body else "")))

# 17. POST /auth/me/change-password (use a temp password then change back for test)
code, body = req("POST", f"{API}/auth/me/change-password", {"current_password": "SuperAdmin1!", "new_password": "TempPass1!"}, token=token)
rows.append(("POST /auth/me/change-password", code, code == 200, "updated" if code == 200 else (body[:60] if body else "")))
if code == 200:
    req("POST", f"{API}/auth/me/change-password", {"current_password": "TempPass1!", "new_password": "SuperAdmin1!"}, token=token)

# 18. POST /auth/logout
code, body = req("POST", f"{API}/auth/logout", token=token)
rows.append(("POST /auth/logout", code, code == 200, body[:40] if body else ""))

# 19. POST /auth/refresh
code, body = req("POST", f"{API}/auth/refresh", {"refresh_token": refresh_token}) if refresh_token else (None, "no refresh token")
rows.append(("POST /auth/refresh", code, code == 200 if code else False, "new tokens" if code == 200 else (body[:60] if body else "")))

# 20. DELETE /users/:id (soft deactivate)
if admin_token and member_user_id:
    code, body = req("DELETE", f"{API}/users/{member_user_id}", token=admin_token)
    rows.append(("DELETE /users/:id (deactivate)", code, code == 200, "deactivated" if code == 200 else (body[:60] if body else "")))

# Print table
print("\n" + "=" * 100)
print("API TEST RESULTS")
print("=" * 100)
print(f"{'API':<40} {'Status':<8} {'Works':<8} {'Note'}")
print("-" * 100)
for api, status, works, note in rows:
    st = str(status) if status is not None else "N/A"
    w = "Yes" if works else "No"
    print(f"{api:<40} {st:<8} {w:<8} {(note or '')[:50]}")
print("=" * 100)
passed = sum(1 for _, _, w, _ in rows if w)
print(f"Passed: {passed}/{len(rows)}")
sys.exit(0 if passed == len(rows) else 1)
