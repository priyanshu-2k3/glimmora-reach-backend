# Test all APIs and output a results table. Run from project root with server running.
# Usage: .\scripts\test_all_apis.ps1

$base = "http://127.0.0.1:8000/api/v1"
$results = @()
$token = $null
$refreshToken = $null
$orgId = $null
$adminToken = $null
$inviteToken = $null
$userId = $null

function Test-Api {
    param($Name, $Method, $Uri, $Body = $null, $Headers = @{}, $ExpectSuccess = $true)
    try {
        $params = @{ Uri = $Uri; Method = $Method; UseBasicParsing = $true; TimeoutSec = 15 }
        if ($Headers.Count -gt 0) { $params.Headers = $Headers }
        if ($Body) { $params.Body = $Body; $params.ContentType = "application/json" }
        $r = Invoke-WebRequest @params
        $ok = $r.StatusCode -ge 200 -and $r.StatusCode -lt 300
        $script:results += [PSCustomObject]@{ API = $Name; Status = $r.StatusCode; Works = $ok; Note = $r.Content.Substring(0, [Math]::Min(80, $r.Content.Length)) }
        return @{ ok = $ok; status = $r.StatusCode; content = $r.Content }
    } catch {
        $status = $_.Exception.Response.StatusCode.value__
        if (-not $status) { $status = "Error" }
        $script:results += [PSCustomObject]@{ API = $Name; Status = $status; Works = $false; Note = $_.Exception.Message.Substring(0, [Math]::Min(80, $_.Exception.Message.Length)) }
        return @{ ok = $false; status = $status; content = $null }
    }
}

# 1. Health
$r = Test-Api -Name "GET /health" -Method GET -Uri "http://127.0.0.1:8000/health"

# 2. Login (Super Admin)
$r = Test-Api -Name "POST /auth/login (Super Admin)" -Method POST -Uri "$base/auth/login" -Body '{"email":"superadmin@test.com","password":"SuperAdmin1!"}'
if ($r.ok -and $r.content) {
    $json = $r.content | ConvertFrom-Json
    $token = $json.access_token
    $refreshToken = $json.refresh_token
}

# 3. GET /auth/me
$r = Test-Api -Name "GET /auth/me" -Method GET -Uri "$base/auth/me" -Headers @{ Authorization = "Bearer $token" }

# 4. GET /auth/me/spec
$r = Test-Api -Name "GET /auth/me/spec" -Method GET -Uri "$base/auth/me/spec" -Headers @{ Authorization = "Bearer $token" }

# 5. Register (optional user)
$r = Test-Api -Name "POST /auth/register" -Method POST -Uri "$base/auth/register" -Body '{"first_name":"Curler","last_name":"Test","email":"curler@test.com","password":"Password1!"}'

# 6. POST /organizations
$r = Test-Api -Name "POST /organizations" -Method POST -Uri "$base/organizations" -Body '{"name":"Test Org"}' -Headers @{ Authorization = "Bearer $token" }
if ($r.ok -and $r.content) {
    $json = $r.content | ConvertFrom-Json
    $orgId = $json.id
}

# 7. GET /organizations
$r = Test-Api -Name "GET /organizations" -Method GET -Uri "$base/organizations" -Headers @{ Authorization = "Bearer $token" }

# 8. GET /organizations/:id
if ($orgId) {
    $r = Test-Api -Name "GET /organizations/:id" -Method GET -Uri "$base/organizations/$orgId" -Headers @{ Authorization = "Bearer $token" }
}

# 9. POST /users/create-admin
if ($orgId) {
    $r = Test-Api -Name "POST /users/create-admin" -Method POST -Uri "$base/users/create-admin" -Body "{`"first_name`":`"Org`",`"last_name`":`"Admin`",`"email`":`"admin@test.com`",`"password`":`"AdminPass1!`",`"organization_id`":`"$orgId`"}" -Headers @{ Authorization = "Bearer $token" }
}

# 10. Login as Admin
$r = Test-Api -Name "POST /auth/login (Admin)" -Method POST -Uri "$base/auth/login" -Body '{"email":"admin@test.com","password":"AdminPass1!"}'
if ($r.ok -and $r.content) {
    $json = $r.content | ConvertFrom-Json
    $adminToken = $json.access_token
}

# 11. POST /users/invite
$r = Test-Api -Name "POST /users/invite" -Method POST -Uri "$base/users/invite" -Body '{"email":"member@test.com","role":"CAMPAIGN_MANAGER"}' -Headers @{ Authorization = "Bearer $adminToken" }
if ($r.ok -and $r.content) {
    $json = $r.content | ConvertFrom-Json
    $inviteToken = $json.token
}

# 12. GET /users
$r = Test-Api -Name "GET /users" -Method GET -Uri "$base/users" -Headers @{ Authorization = "Bearer $adminToken" }
if ($r.ok -and $r.content) {
    $arr = $r.content | ConvertFrom-Json
    if ($arr -and $arr.Count -gt 0) { $userId = $arr[0].id }
}

# 13. POST /auth/accept-invite
if ($inviteToken) {
    $body = "{`"token`":`"$inviteToken`",`"first_name`":`"Member`",`"last_name`":`"User`",`"password`":`"MemberPass1!`"}"
    $r = Test-Api -Name "POST /auth/accept-invite" -Method POST -Uri "$base/auth/accept-invite" -Body $body
}

# 14. PUT /auth/profile
$r = Test-Api -Name "PUT /auth/profile" -Method PUT -Uri "$base/auth/profile" -Body '{"first_name":"Super","language":"en"}' -Headers @{ Authorization = "Bearer $token" }

# 15. POST /auth/logout
$r = Test-Api -Name "POST /auth/logout" -Method POST -Uri "$base/auth/logout" -Headers @{ Authorization = "Bearer $token" }

# 16. POST /auth/refresh
$r = Test-Api -Name "POST /auth/refresh" -Method POST -Uri "$base/auth/refresh" -Body "{`"refresh_token`":`"$refreshToken`"}"

# Output table
$results | Format-Table -AutoSize
$results | Export-Csv -Path "scripts\api_test_results.csv" -NoTypeInformation
Write-Host "Results also saved to scripts\api_test_results.csv"
