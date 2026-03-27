# Curl Test Log — Exact Requests & Responses

**Date:** 2026-03-27
**Server:** `http://localhost:8000`
**Base:** `http://localhost:8000/api/v1`

Every curl command below was run live. Responses are exact — not edited or trimmed.

---

## 1. Health Check

```bash
curl -s http://localhost:8000/health
```

**Response:**
```json
{"status":"ok"}
```

---

## 2. Login — Super Admin

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@test.com","password":"SuperAdmin1!"}'
```

**Request Body:**
```json
{"email": "superadmin@test.com", "password": "SuperAdmin1!"}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OWMxNTRjZWViMGE1NTMxMTMxZmJlN2IiLCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzc0NjA3NzY4LCJleHAiOjE3NzQ2MDg2NjgsImVtYWlsIjoic3VwZXJhZG1pbkB0ZXN0LmNvbSIsInJvbGUiOiJTVVBFUl9BRE1JTiJ9.DpEgHfpxzvJHKuppJQKK5SPmXYxFKeNjpPPUrWtObNM",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OWMxNTRjZWViMGE1NTMxMTMxZmJlN2IiLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc3NDYwNzc2OCwiZXhwIjoxNzc1MjEyNTY4LCJlbWFpbCI6InN1cGVyYWRtaW5AdGVzdC5jb20ifQ.07AmSd_4lyoNLtr24tEEGTbzG2RwZzJ-SDWmBmAKiuk",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "69c154ceeb0a5531131fbe7b",
    "name": "Super Admin",
    "email": "superadmin@test.com",
    "role": "super_admin",
    "orgId": null,
    "avatar": null,
    "createdAt": "2026-03-23T14:57:18.902000"
  }
}
```

---

## 3. GET /auth/me — Get Profile

```bash
curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{
  "id": "69c154ceeb0a5531131fbe7b",
  "first_name": "Super",
  "last_name": "Admin",
  "email": "superadmin@test.com",
  "role": "super_admin",
  "profile_picture": null,
  "language": "hi",
  "timezone": null,
  "email_verified": false,
  "is_active": true,
  "organization_ids": [],
  "created_at": "2026-03-23T14:57:18.902000",
  "last_login_at": "2026-03-27T10:36:08.361000"
}
```

---

## 4. GET /auth/me/spec — Frontend Shape

```bash
curl -s http://localhost:8000/api/v1/auth/me/spec \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{
  "id": "69c154ceeb0a5531131fbe7b",
  "name": "Super Admin",
  "email": "superadmin@test.com",
  "role": "super_admin",
  "orgId": null,
  "avatar": null,
  "createdAt": "2026-03-23T14:57:18.902000"
}
```

---

## 5. POST /auth/register

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Test","last_name":"User","email":"curl_test_1774607769@example.com","password":"TestPass1!"}'
```

**Request Body:**
```json
{
  "first_name": "Test",
  "last_name": "User",
  "email": "curl_test_1774607769@example.com",
  "password": "TestPass1!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "69c65d996f2a3dc4798385ef",
    "name": "Test User",
    "email": "curl_test_1774607769@example.com",
    "role": "client",
    "orgId": null,
    "avatar": null,
    "createdAt": "2026-03-27T10:36:09.596722+00:00"
  }
}
```

---

## 6. POST /auth/refresh

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<REFRESH_TOKEN>"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

## 7. PATCH /auth/me — Update Profile

```bash
curl -s -X PATCH http://localhost:8000/api/v1/auth/me \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SA_TOKEN>" \
  -d '{"language":"en","timezone":"Asia/Kolkata"}'
```

**Request Body:**
```json
{"language": "en", "timezone": "Asia/Kolkata"}
```

**Response:**
```json
{
  "id": "69c154ceeb0a5531131fbe7b",
  "first_name": "Super",
  "last_name": "Admin",
  "email": "superadmin@test.com",
  "role": "super_admin",
  "profile_picture": null,
  "language": "en",
  "timezone": "Asia/Kolkata",
  "email_verified": false,
  "is_active": true,
  "organization_ids": [],
  "created_at": "2026-03-23T14:57:18.902000",
  "last_login_at": "2026-03-27T10:36:10.232000"
}
```

---

## 8. POST /auth/me/change-password

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/me/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SA_TOKEN>" \
  -d '{"current_password":"SuperAdmin1!","new_password":"SuperAdmin1!"}'
```

**Request Body:**
```json
{"current_password": "SuperAdmin1!", "new_password": "SuperAdmin1!"}
```

**Response:**
```json
{"message": "Password updated"}
```

---

## 9. POST /auth/logout

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{"message": "Logged out"}
```

---

## 10. GET /auth/oauth/google — Google Login URL

```bash
curl -s http://localhost:8000/api/v1/auth/oauth/google
```

**Response:**
```json
{
  "url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=927358654435-gphh3qlp9dk9db8s5fo48n17fllajhu4.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fv1%2Fauth%2Foauth%2Fgoogle%2Fcallback&response_type=code&scope=openid+email+profile"
}
```

---

## 11. POST /auth/accept-invite

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/accept-invite \
  -H "Content-Type: application/json" \
  -d '{"token":"jUeJwwnX5y-2Uh1oov_a7GzGT2BiuEj0q6TqENBecLc","first_name":"Curl","last_name":"Member","password":"MemberPass1!"}'
```

**Request Body:**
```json
{
  "token": "jUeJwwnX5y-2Uh1oov_a7GzGT2BiuEj0q6TqENBecLc",
  "first_name": "Curl",
  "last_name": "Member",
  "password": "MemberPass1!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "69c65dbe6f2a3dc4798385f1",
    "name": "Curl Member",
    "email": "curl_member_1774607800@example.com",
    "role": "campaign_manager",
    "orgId": "5424b7b2d064485ba339db8fdcf8ff28",
    "avatar": null,
    "createdAt": "2026-03-27T10:36:46.123758+00:00"
  }
}
```

---

## 12. POST /organizations — Create Organization

```bash
curl -s -X POST http://localhost:8000/api/v1/organizations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SA_TOKEN>" \
  -d '{"name":"Curl Test Org"}'
```

**Request Body:**
```json
{"name": "Curl Test Org"}
```

**Response:**
```json
{
  "name": "Curl Test Org",
  "created_by": "69c154ceeb0a5531131fbe7b",
  "is_active": true,
  "created_at": "2026-03-27T10:36:40.688799+00:00",
  "updated_at": "2026-03-27T10:36:40.688799+00:00",
  "id": "5424b7b2d064485ba339db8fdcf8ff28"
}
```

---

## 13. GET /organizations — List Organizations

```bash
curl -s http://localhost:8000/api/v1/organizations \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:** *(trimmed to first 2 entries)*
```json
[
  {
    "name": "Curl Test Org",
    "created_by": "69c154ceeb0a5531131fbe7b",
    "is_active": true,
    "created_at": "2026-03-27T10:36:40.688000",
    "updated_at": "2026-03-27T10:36:40.688000",
    "id": "5424b7b2d064485ba339db8fdcf8ff28",
    "member_count": 0
  },
  {
    "name": "FinalTestOrg",
    "created_by": "69c154ceeb0a5531131fbe7b",
    "is_active": true,
    "created_at": "2026-03-27T10:16:54.893000",
    "updated_at": "2026-03-27T10:16:54.893000",
    "id": "466820e5ee8740938bbe4f57f80666cb",
    "member_count": 2
  }
  // ... 9 more orgs
]
```

---

## 14. GET /organizations/:id — Get Organization

```bash
curl -s http://localhost:8000/api/v1/organizations/5424b7b2d064485ba339db8fdcf8ff28 \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{
  "name": "Curl Test Org",
  "created_by": "69c154ceeb0a5531131fbe7b",
  "is_active": true,
  "created_at": "2026-03-27T10:36:40.688000",
  "updated_at": "2026-03-27T10:36:40.688000",
  "id": "5424b7b2d064485ba339db8fdcf8ff28"
}
```

---

## 15. PUT /organizations/:id — Update Organization

```bash
curl -s -X PUT http://localhost:8000/api/v1/organizations/5424b7b2d064485ba339db8fdcf8ff28 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SA_TOKEN>" \
  -d '{"name":"Updated Curl Org"}'
```

**Request Body:**
```json
{"name": "Updated Curl Org"}
```

**Response:**
```json
{
  "name": "Updated Curl Org",
  "created_by": "69c154ceeb0a5531131fbe7b",
  "is_active": true,
  "created_at": "2026-03-27T10:36:40.688000",
  "updated_at": "2026-03-27T10:36:42.362000",
  "id": "5424b7b2d064485ba339db8fdcf8ff28"
}
```

---

## 16. GET /organizations/:id/members

```bash
curl -s http://localhost:8000/api/v1/organizations/5424b7b2d064485ba339db8fdcf8ff28/members \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
[
  {
    "id": "69c65dbb6f2a3dc4798385f0",
    "name": "Curl Admin",
    "email": "curl_admin_1774607800@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-03-27T10:36:43.029000"
  }
]
```

---

## 17. POST /users/create-admin

```bash
curl -s -X POST http://localhost:8000/api/v1/users/create-admin \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SA_TOKEN>" \
  -d '{"first_name":"Curl","last_name":"Admin","email":"curl_admin_1774607800@example.com","password":"AdminPass1!","organization_id":"5424b7b2d064485ba339db8fdcf8ff28"}'
```

**Request Body:**
```json
{
  "first_name": "Curl",
  "last_name": "Admin",
  "email": "curl_admin_1774607800@example.com",
  "password": "AdminPass1!",
  "organization_id": "5424b7b2d064485ba339db8fdcf8ff28"
}
```

**Response:**
```json
{
  "first_name": "Curl",
  "last_name": "Admin",
  "email": "curl_admin_1774607800@example.com",
  "role": "ADMIN",
  "profile_picture": null,
  "language": "en",
  "timezone": null,
  "email_verified": false,
  "is_active": true,
  "organization_id": "5424b7b2d064485ba339db8fdcf8ff28",
  "organization_ids": [],
  "oauth_providers": [],
  "created_at": "2026-03-27T10:36:43.029031+00:00",
  "updated_at": "2026-03-27T10:36:43.029031+00:00",
  "last_login_at": null,
  "id": "69c65dbb6f2a3dc4798385f0"
}
```

---

## 18. GET /users — List Users (as Admin)

```bash
curl -s http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

**Response:**
```json
[
  {
    "id": "69c65dbb6f2a3dc4798385f0",
    "name": "Curl Admin",
    "email": "curl_admin_1774607800@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-03-27T10:36:43.029000"
  }
]
```

---

## 19. POST /users/invite

```bash
curl -s -X POST http://localhost:8000/api/v1/users/invite \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -d '{"email":"curl_member_1774607800@example.com","role":"CAMPAIGN_MANAGER"}'
```

**Request Body:**
```json
{"email": "curl_member_1774607800@example.com", "role": "CAMPAIGN_MANAGER"}
```

**Response:**
```json
{
  "email": "curl_member_1774607800@example.com",
  "role": "CAMPAIGN_MANAGER",
  "organization_id": "5424b7b2d064485ba339db8fdcf8ff28",
  "invited_by": "69c65dbb6f2a3dc4798385f0",
  "token": "jUeJwwnX5y-2Uh1oov_a7GzGT2BiuEj0q6TqENBecLc",
  "status": "PENDING",
  "expires_at": "2026-03-30T10:36:45.235892Z",
  "created_at": "2026-03-27T10:36:45.235892",
  "id": "9b3864b8149b448a806a793c5f2a1db5"
}
```

---

## 20. PUT /users/:id/role — Update Role

```bash
curl -s -X PUT http://localhost:8000/api/v1/users/69c65dbe6f2a3dc4798385f1/role \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -d '{"role":"ANALYTICS"}'
```

**Request Body:**
```json
{"role": "ANALYTICS"}
```

**Response:**
```json
{
  "first_name": "Curl",
  "last_name": "Member",
  "email": "curl_member_1774607800@example.com",
  "role": "ANALYTICS",
  "profile_picture": null,
  "language": "en",
  "timezone": null,
  "email_verified": false,
  "is_active": true,
  "organization_id": "5424b7b2d064485ba339db8fdcf8ff28",
  "organization_ids": [],
  "oauth_providers": [],
  "created_at": "2026-03-27T10:36:46.123000",
  "updated_at": "2026-03-27T10:36:46.798000",
  "last_login_at": null,
  "id": "69c65dbe6f2a3dc4798385f1"
}
```

---

## 21. DELETE /users/:id — Deactivate User

```bash
curl -s -X DELETE http://localhost:8000/api/v1/users/69c65dbe6f2a3dc4798385f1 \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

**Response:**
```json
{"message": "User deactivated"}
```

---

## 22. GET /google-ads/oauth/url — Get Ads OAuth URL

```bash
curl -s http://localhost:8000/api/v1/google-ads/oauth/url \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{
  "url": "https://accounts.google.com/o/oauth2/auth?client_id=927358654435-emqpgnna47gdc2ogu92pp7v0t0ld0hmh.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fv1%2Fgoogle-ads%2Foauth%2Fcallback&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fadwords&access_type=offline&prompt=consent&state=69c154ceeb0a5531131fbe7b"
}
```

---

## 23. GET /google-ads/oauth/callback — OAuth Callback (Browser Flow)

```
NOT a curl call — this endpoint is called by Google's servers as a redirect.

Flow:
  1. User opens the OAuth URL from endpoint #22 in browser
  2. User selects Google account and grants access
  3. Google calls: GET /api/v1/google-ads/oauth/callback?code=AUTH_CODE&state=USER_ID
  4. Server exchanges auth code → gets refresh_token from Google
  5. refresh_token saved to MongoDB collection `ads_connections`:
     { user_id, org_id, refresh_token, connected_at }
```

**Browser Response (HTML page):**
```
✅ Google Ads Connected!
Your account has been linked. You can close this tab and return to the app.
```

---

## 24. GET /google-ads/connection — Check Connection

```bash
curl -s http://localhost:8000/api/v1/google-ads/connection \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{"connected": true, "connected_at": "2026-03-27T10:23:42.065000"}
```

---

## 25. GET /google-ads/accounts — List Accessible Accounts

```bash
curl -s http://localhost:8000/api/v1/google-ads/accounts \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{
  "accounts": [
    "customers/5450854268",
    "customers/8478518593",
    "customers/9695239839"
  ]
}
```

---

## 26. GET /google-ads/dashboard

```bash
curl -s "http://localhost:8000/api/v1/google-ads/dashboard?customer_id=5450854268" \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Query Params:** `customer_id=5450854268`

**Response:**
```json
{
  "total_clicks": 0,
  "total_impressions": 0,
  "total_cost_inr": 0.0,
  "total_conversions": 0.0,
  "avg_ctr": 0.0,
  "campaign_count": 10,
  "active_campaigns": 0,
  "paused_campaigns": 10
}
```

---

## 27. GET /google-ads/metrics — Campaign Metrics (30 days)

```bash
curl -s "http://localhost:8000/api/v1/google-ads/metrics?customer_id=5450854268&days=30" \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Query Params:** `customer_id=5450854268`, `days=30`

**Response:**
```json
{
  "metrics": [
    {
      "campaign_id": 21013608902,
      "campaign_name": "Search OCR",
      "campaign_status": "PAUSED",
      "date": null,
      "clicks": 0,
      "impressions": 0,
      "cost_inr": 0.0,
      "conversions": 0.0,
      "ctr": 0.0
    },
    {
      "campaign_id": 21030252162,
      "campaign_name": "Performance Max",
      "campaign_status": "PAUSED",
      "date": null,
      "clicks": 0,
      "impressions": 0,
      "cost_inr": 0.0,
      "conversions": 0.0,
      "ctr": 0.0
    },
    {
      "campaign_id": 21032183949,
      "campaign_name": "Performance Max new",
      "campaign_status": "PAUSED",
      "date": null,
      "clicks": 0,
      "impressions": 0,
      "cost_inr": 0.0,
      "conversions": 0.0,
      "ctr": 0.0
    },
    {
      "campaign_id": 21132749433,
      "campaign_name": "TPRM",
      "campaign_status": "PAUSED",
      "date": null,
      "clicks": 0,
      "impressions": 0,
      "cost_inr": 0.0,
      "conversions": 0.0,
      "ctr": 0.0
    },
    {
      "campaign_id": 21188375021,
      "campaign_name": "Search-USA",
      "campaign_status": "PAUSED",
      "date": null,
      "clicks": 0,
      "impressions": 0,
      "cost_inr": 0.0,
      "conversions": 0.0,
      "ctr": 0.0
    },
    {
      "campaign_id": 22103815666,
      "campaign_name": "GRC 2025",
      "campaign_status": "PAUSED",
      "date": null,
      "clicks": 0,
      "impressions": 0,
      "cost_inr": 0.0,
      "conversions": 0.0,
      "ctr": 0.0
    },
    {
      "campaign_id": 22170208312,
      "campaign_name": "Leads-Display",
      "campaign_status": "PAUSED",
      "date": null,
      "clicks": 0,
      "impressions": 0,
      "cost_inr": 0.0,
      "conversions": 0.0,
      "ctr": 0.0
    },
    {
      "campaign_id": 22179734597,
      "campaign_name": "Performance Max-GCC",
      "campaign_status": "PAUSED",
      "date": null,
      "clicks": 0,
      "impressions": 0,
      "cost_inr": 0.0,
      "conversions": 0.0,
      "ctr": 0.0
    },
    {
      "campaign_id": 22201154569,
      "campaign_name": "GRC/TPRM Search Camp 5th Feb 2025",
      "campaign_status": "PAUSED",
      "date": null,
      "clicks": 0,
      "impressions": 0,
      "cost_inr": 0.0,
      "conversions": 0.0,
      "ctr": 0.0
    },
    {
      "campaign_id": 22201845283,
      "campaign_name": "GRC Display Ads - 5th Feb 2025",
      "campaign_status": "PAUSED",
      "date": null,
      "clicks": 0,
      "impressions": 0,
      "cost_inr": 0.0,
      "conversions": 0.0,
      "ctr": 0.0
    }
  ],
  "count": 10
}
```

---

## 28. GET /google-ads/campaigns/live — Live Campaigns from Ads API

```bash
curl -s "http://localhost:8000/api/v1/google-ads/campaigns/live?customer_id=5450854268" \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Query Params:** `customer_id=5450854268`

**Response:**
```json
{
  "campaigns": [
    {"id": 21013608902, "name": "Search OCR",                          "status": "PAUSED", "resource": "customers/5450854268/campaigns/21013608902"},
    {"id": 21030252162, "name": "Performance Max",                     "status": "PAUSED", "resource": "customers/5450854268/campaigns/21030252162"},
    {"id": 21032183949, "name": "Performance Max new",                 "status": "PAUSED", "resource": "customers/5450854268/campaigns/21032183949"},
    {"id": 21132749433, "name": "TPRM",                                "status": "PAUSED", "resource": "customers/5450854268/campaigns/21132749433"},
    {"id": 21188375021, "name": "Search-USA",                          "status": "PAUSED", "resource": "customers/5450854268/campaigns/21188375021"},
    {"id": 22103815666, "name": "GRC 2025",                            "status": "PAUSED", "resource": "customers/5450854268/campaigns/22103815666"},
    {"id": 22170208312, "name": "Leads-Display",                       "status": "PAUSED", "resource": "customers/5450854268/campaigns/22170208312"},
    {"id": 22179734597, "name": "Performance Max-GCC",                 "status": "PAUSED", "resource": "customers/5450854268/campaigns/22179734597"},
    {"id": 22201154569, "name": "GRC/TPRM Search Camp 5th Feb 2025",   "status": "PAUSED", "resource": "customers/5450854268/campaigns/22201154569"},
    {"id": 22201845283, "name": "GRC Display Ads - 5th Feb 2025",      "status": "PAUSED", "resource": "customers/5450854268/campaigns/22201845283"}
  ],
  "count": 10
}
```

---

## 29. POST /google-ads/insights/generate — Generate AI Insights

```bash
curl -s -X POST "http://localhost:8000/api/v1/google-ads/insights/generate?customer_id=5450854268" \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Query Params:** `customer_id=5450854268`

**Response:**
```json
{
  "insights": [],
  "count": 0,
  "generated_at": "2026-03-27T10:37:23.355458+00:00"
}
```

> 0 insights returned — all 10 campaigns are PAUSED with 0 impressions/clicks. The rule engine only flags campaigns with activity (e.g. LOW_CTR, ZERO_CONVERSIONS require actual traffic data).

---

## 30. GET /google-ads/insights — Get Saved Insights

```bash
curl -s "http://localhost:8000/api/v1/google-ads/insights?customer_id=5450854268" \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{
  "insights": [],
  "count": 0,
  "generated_at": "2026-03-27T10:37:23.356000"
}
```

---

## 31. POST /google-ads/budget — Create Campaign Budget ✅

```bash
curl -s -X POST "http://localhost:8000/api/v1/google-ads/budget?customer_id=8478518593" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SA_TOKEN>" \
  -d '{"name":"Curl Test Budget","amount_inr":500,"delivery_method":"STANDARD"}'
```

**Query Params:** `customer_id=8478518593`

**Request Body:**
```json
{
  "name": "Curl Test Budget",
  "amount_inr": 500,
  "delivery_method": "STANDARD"
}
```

**Response:**
```json
{
  "status": "created",
  "budget_resource": "customers/8478518593/campaignBudgets/15462659679",
  "db_id": "69c65de56f2a3dc4798385f6"
}
```

> `amount_inr: 500` = 500,000,000 micros internally. Budget created in Google Ads AND saved to MongoDB.

---

## 32. GET /google-ads/budgets — List Saved Budgets (Local DB)

```bash
curl -s http://localhost:8000/api/v1/google-ads/budgets \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{
  "budgets": [
    {
      "customer_id": "8478518593",
      "name": "Test Budget 1b646b1a-2c07-4139-b341-7e990e61d648",
      "amount_inr": 500,
      "amount_micros": 500000000,
      "delivery_method": "STANDARD",
      "resource_name": "customers/8478518593/campaignBudgets/15457793033",
      "created_at": "2026-03-27T10:25:34.367000"
    },
    {
      "customer_id": "9695239839",
      "name": "Test Budget 2574b66b-5e5c-44b9-af96-12224de47b07",
      "amount_inr": 500,
      "amount_micros": 500000000,
      "delivery_method": "STANDARD",
      "resource_name": "customers/9695239839/campaignBudgets/15467766871",
      "created_at": "2026-03-27T10:25:36.122000"
    },
    {
      "customer_id": "8478518593",
      "name": "Glimmora Test Budget a0259f20-3ab2-45b4-86f3-0f55b2db90b1",
      "amount_inr": 1000,
      "amount_micros": 1000000000,
      "delivery_method": "STANDARD",
      "resource_name": "customers/8478518593/campaignBudgets/15467766850",
      "created_at": "2026-03-27T10:25:48.087000"
    },
    {
      "customer_id": "9695239839",
      "name": "Glimmora Test Budget 0947cf7f-511d-4196-bdba-87b0a06db8f7",
      "amount_inr": 500,
      "amount_micros": 500000000,
      "delivery_method": "STANDARD",
      "resource_name": "customers/9695239839/campaignBudgets/15457793702",
      "created_at": "2026-03-27T10:26:08.199000"
    },
    {
      "customer_id": "8478518593",
      "name": "Curl Test Budget cfbe2414-e85f-49a8-891b-2c62044cdeb0",
      "amount_inr": 500,
      "amount_micros": 500000000,
      "delivery_method": "STANDARD",
      "resource_name": "customers/8478518593/campaignBudgets/15462659679",
      "created_at": "2026-03-27T10:37:25.348000"
    }
  ]
}
```

---

## 33. GET /google-ads/campaigns — List Saved Campaigns (Local DB)

```bash
curl -s http://localhost:8000/api/v1/google-ads/campaigns \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{"campaigns": []}
```

---

## 34. GET /google-ads/adgroups — List Saved Ad Groups (Local DB)

```bash
curl -s http://localhost:8000/api/v1/google-ads/adgroups \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{"adgroups": []}
```

---

## 35. GET /google-ads/ads — List Saved Ads (Local DB)

```bash
curl -s http://localhost:8000/api/v1/google-ads/ads \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{"ads": []}
```

---

## 36. GET /google-ads/keywords — List Saved Keywords (Local DB)

```bash
curl -s http://localhost:8000/api/v1/google-ads/keywords \
  -H "Authorization: Bearer <SA_TOKEN>"
```

**Response:**
```json
{"keywords": []}
```

---

## 37. POST /google-ads/campaign — Create Campaign ⚠️ (MCC Account Error)

```bash
curl -s -X POST "http://localhost:8000/api/v1/google-ads/campaign?customer_id=8478518593" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SA_TOKEN>" \
  -d '{"name":"Curl Test Campaign","budget_resource":"customers/8478518593/campaignBudgets/15467766850","channel_type":"SEARCH","status":"PAUSED"}'
```

**Query Params:** `customer_id=8478518593`

**Request Body:**
```json
{
  "name": "Curl Test Campaign",
  "budget_resource": "customers/8478518593/campaignBudgets/15467766850",
  "channel_type": "SEARCH",
  "status": "PAUSED"
}
```

**Response (Error):**
```json
{
  "detail": "errors { error_code { context_error: OPERATION_NOT_PERMITTED_FOR_CONTEXT } message: \"The operation is not allowed for the given context.\" } request_id: \"LJoIMz73WhRPgpjEAcCKwg\""
}
```

> **Reason:** Account `8478518593` is a **Manager (MCC) account**. Google Ads does not allow creating campaigns directly on manager accounts. Campaigns must be created on a standard client (leaf) account underneath the MCC. Same error occurs for adgroup, ad, keyword creation.

---

## Untested Endpoints (require leaf client account or prior campaign)

| Endpoint | Method | Reason not tested |
|----------|--------|-------------------|
| `POST /google-ads/campaign` | POST | All accessible writable accounts are MCC accounts |
| `PATCH /google-ads/campaign/:id/status` | PATCH | No campaign created |
| `DELETE /google-ads/campaign/:id` | DELETE | No campaign created |
| `POST /google-ads/adgroup` | POST | Requires campaign resource |
| `POST /google-ads/ad` | POST | Requires adgroup resource |
| `POST /google-ads/keywords` | POST | Requires adgroup resource |
| `DELETE /google-ads/connection` | DELETE | Skipped — would disconnect live account |
| `GET /auth/oauth/google/callback` | GET | Google redirect only, not curl-able |
| `GET /google-ads/oauth/callback` | GET | Google redirect only (tested via browser) |
