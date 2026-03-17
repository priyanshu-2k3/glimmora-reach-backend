@echo off
setlocal DisableDelayedExpansion
set BASE=http://127.0.0.1:8000
set API=%BASE%/api/v1
set RES=%~dp0curl_res.json
set STATUS_FILE=%~dp0curl_status.txt
set "BODYFILE=%~dp0change_back_password.json"
set TOKEN=
set REFRESH_TOKEN=
set ORG_ID=
set ADMIN_TOKEN=
set INVITE_TOKEN=
set MEMBER_USER_ID=
set USER_ID_FOR_ROLE=

echo.
echo ========================================
echo API TEST RESULTS (curl via CMD)
echo ========================================
echo API                                    Status  Works   Note
echo ----------------------------------------

:: 1. GET /health
curl -s -o "%RES%" -w "%%{http_code}" "%BASE%/health" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
if %S%==200 (echo GET /health                            %S%      Yes     ok) else (echo GET /health                            %S%      No      fail)

:: 2. POST /auth/login (Super Admin)
curl -s -o "%RES%" -w "%%{http_code}" -X POST "%API%/auth/login" -H "Content-Type: application/json" -d "{\"email\":\"superadmin@test.com\",\"password\":\"SuperAdmin1!\"}" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
for /f "delims=" %%t in ('powershell -NoProfile -Command "(Get-Content -Raw '%RES%' | ConvertFrom-Json).access_token" 2^>nul') do set "TOKEN=%%t"
for /f "delims=" %%t in ('powershell -NoProfile -Command "(Get-Content -Raw '%RES%' | ConvertFrom-Json).refresh_token" 2^>nul') do set "REFRESH_TOKEN=%%t"
if %S%==200 (echo POST /auth/login - Super Admin            %S%      Yes     tokens) else (echo POST /auth/login - Super Admin            %S%      No      fail)

:: 3. GET /auth/me
curl -s -o "%RES%" -w "%%{http_code}" -X GET "%API%/auth/me" -H "Authorization: Bearer %TOKEN%" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
if %S%==200 (echo GET /auth/me                             %S%      Yes     profile) else (echo GET /auth/me                             %S%      No      fail)

:: 4. GET /auth/me/spec
curl -s -o "%RES%" -w "%%{http_code}" -X GET "%API%/auth/me/spec" -H "Authorization: Bearer %TOKEN%" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
if %S%==200 (echo GET /auth/me/spec                        %S%      Yes     spec) else (echo GET /auth/me/spec                        %S%      No      fail)

:: 5. POST /auth/register
curl -s -o "%RES%" -w "%%{http_code}" -X POST "%API%/auth/register" -H "Content-Type: application/json" -d "{\"first_name\":\"Curler\",\"last_name\":\"Test\",\"email\":\"curler@test.com\",\"password\":\"Password1!\"}" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
if %S%==200 (echo POST /auth/register                      %S%      Yes     tokens) else (if %S%==400 (echo POST /auth/register                      %S%      Yes     already registered) else (echo POST /auth/register                      %S%      No      fail))

:: 6. POST /organizations
curl -s -o "%RES%" -w "%%{http_code}" -X POST "%API%/organizations" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"name\":\"Test Org\"}" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
for /f "delims=" %%i in ('powershell -NoProfile -Command "(Get-Content -Raw '%RES%' | ConvertFrom-Json).id" 2^>nul') do set "ORG_ID=%%i"
if %S%==201 (echo POST /organizations                     %S%      Yes     created) else (if %S%==200 (echo POST /organizations                     %S%      Yes     created) else (echo POST /organizations                     %S%      No      fail))

:: 7. GET /organizations
curl -s -o "%RES%" -w "%%{http_code}" -X GET "%API%/organizations" -H "Authorization: Bearer %TOKEN%" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
if %S%==200 (echo GET /organizations                       %S%      Yes     list) else (echo GET /organizations                       %S%      No      fail)

:: 8. GET /organizations/:id
if defined ORG_ID (
  curl -s -o "%RES%" -w "%%{http_code}" -X GET "%API%/organizations/%ORG_ID%" -H "Authorization: Bearer %TOKEN%" 1>"%STATUS_FILE%"
  set /p S=<"%STATUS_FILE%"
  if %S%==200 (echo GET /organizations/:id                   %S%      Yes     detail) else (echo GET /organizations/:id                   %S%      No      fail)
)

:: 9. POST /users/create-admin
if defined ORG_ID (
  curl -s -o "%RES%" -w "%%{http_code}" -X POST "%API%/users/create-admin" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"first_name\":\"Org\",\"last_name\":\"Admin\",\"email\":\"admin@test.com\",\"password\":\"AdminPass1!\",\"organization_id\":\"%ORG_ID%\"}" 1>"%STATUS_FILE%"
  set /p S=<"%STATUS_FILE%"
  if %S%==201 (echo POST /users/create-admin               %S%      Yes     created) else (if %S%==200 (echo POST /users/create-admin               %S%      Yes     created) else (if %S%==400 (echo POST /users/create-admin               %S%      Yes     already exists) else (echo POST /users/create-admin               %S%      No      fail)))
)

:: 10. POST /auth/login (Admin)
curl -s -o "%RES%" -w "%%{http_code}" -X POST "%API%/auth/login" -H "Content-Type: application/json" -d "{\"email\":\"admin@test.com\",\"password\":\"AdminPass1!\"}" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
for /f "delims=" %%t in ('powershell -NoProfile -Command "(Get-Content -Raw '%RES%' | ConvertFrom-Json).access_token" 2^>nul') do set "ADMIN_TOKEN=%%t"
if %S%==200 (echo POST /auth/login - Admin                  %S%      Yes     tokens) else (echo POST /auth/login - Admin                  %S%      No      fail)

:: 11. POST /users/invite
curl -s -o "%RES%" -w "%%{http_code}" -X POST "%API%/users/invite" -H "Content-Type: application/json" -H "Authorization: Bearer %ADMIN_TOKEN%" -d "{\"email\":\"member@test.com\",\"role\":\"CAMPAIGN_MANAGER\"}" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
for /f "delims=" %%t in ('powershell -NoProfile -Command "(Get-Content -Raw '%RES%' | ConvertFrom-Json).token" 2^>nul') do set "INVITE_TOKEN=%%t"
if %S%==201 (echo POST /users/invite                       %S%      Yes     invite) else (if %S%==200 (echo POST /users/invite                       %S%      Yes     invite) else (if %S%==400 (echo POST /users/invite                       %S%      Yes     user exists) else (echo POST /users/invite                       %S%      No      fail)))

:: 12. POST /auth/accept-invite
if defined INVITE_TOKEN (
  curl -s -o "%RES%" -w "%%{http_code}" -X POST "%API%/auth/accept-invite" -H "Content-Type: application/json" -d "{\"token\":\"%INVITE_TOKEN%\",\"first_name\":\"Member\",\"last_name\":\"User\",\"password\":\"MemberPass1!\"}" 1>"%STATUS_FILE%"
  set /p S=<"%STATUS_FILE%"
  if %S%==200 (echo POST /auth/accept-invite                %S%      Yes     tokens) else (echo POST /auth/accept-invite                %S%      No      fail)
)

:: 13. GET /users
curl -s -o "%RES%" -w "%%{http_code}" -X GET "%API%/users" -H "Authorization: Bearer %ADMIN_TOKEN%" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
for /f "delims=" %%i in ('powershell -NoProfile -Command "$j=Get-Content -Raw '%RES%'|ConvertFrom-Json; $u=$j|Where-Object{$_.email -eq 'member@test.com'}|Select-Object -First 1; if($u){$u.id}" 2^>nul') do set "MEMBER_USER_ID=%%i"
for /f "delims=" %%i in ('powershell -NoProfile -Command "$j=Get-Content -Raw '%RES%'|ConvertFrom-Json; if($j -and $j[0]){$j[0].id}" 2^>nul') do set "USER_ID_FOR_ROLE=%%i"
if not defined USER_ID_FOR_ROLE set USER_ID_FOR_ROLE=%MEMBER_USER_ID%
if %S%==200 (echo GET /users                               %S%      Yes     list) else (echo GET /users                               %S%      No      fail)

:: 14. PUT /organizations/:id
if defined ORG_ID (
  curl -s -o "%RES%" -w "%%{http_code}" -X PUT "%API%/organizations/%ORG_ID%" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"name\":\"Test Org Updated\",\"is_active\":true}" 1>"%STATUS_FILE%"
  set /p S=<"%STATUS_FILE%"
  if %S%==200 (echo PUT /organizations/:id                  %S%      Yes     updated) else (echo PUT /organizations/:id                  %S%      No      fail)
)

:: 15. PUT /users/:id/role
if defined ADMIN_TOKEN if defined USER_ID_FOR_ROLE (
  curl -s -o "%RES%" -w "%%{http_code}" -X PUT "%API%/users/%USER_ID_FOR_ROLE%/role" -H "Content-Type: application/json" -H "Authorization: Bearer %ADMIN_TOKEN%" -d "{\"role\":\"VIEWER\"}" 1>"%STATUS_FILE%"
  set /p S=<"%STATUS_FILE%"
  if %S%==200 (echo PUT /users/:id/role                     %S%      Yes     updated) else (echo PUT /users/:id/role                     %S%      No      fail)
)

:: 16. PUT /auth/profile
curl -s -o "%RES%" -w "%%{http_code}" -X PUT "%API%/auth/profile" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"first_name\":\"Super\",\"language\":\"en\"}" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
if %S%==200 (echo PUT /auth/profile                        %S%      Yes     updated) else (echo PUT /auth/profile                        %S%      No      fail)

:: 17. POST /auth/me/change-password
curl -s -o "%RES%" -w "%%{http_code}" -X POST "%API%/auth/me/change-password" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"current_password\":\"SuperAdmin1!\",\"new_password\":\"TempPass1!\"}" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
if %S%==200 (echo POST /auth/me/change-password             %S%      Yes     updated) else (echo POST /auth/me/change-password             %S%      No      fail)
:: change back
(curl -s -o "%RES%" -w "%%{http_code}" -X POST "%API%/auth/me/change-password" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "@%BODYFILE%" 1>"%STATUS_FILE%") 2>nul

:: 18. POST /auth/logout
curl -s -o "%RES%" -w "%%{http_code}" -X POST "%API%/auth/logout" -H "Authorization: Bearer %TOKEN%" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
if %S%==200 (echo POST /auth/logout                         %S%      Yes     ok) else (echo POST /auth/logout                         %S%      No      fail)

:: 19. POST /auth/refresh
curl -s -o "%RES%" -w "%%{http_code}" -X POST "%API%/auth/refresh" -H "Content-Type: application/json" -d "{\"refresh_token\":\"%REFRESH_TOKEN%\"}" 1>"%STATUS_FILE%"
set /p S=<"%STATUS_FILE%"
if %S%==200 (echo POST /auth/refresh                        %S%      Yes     new tokens) else (echo POST /auth/refresh                        %S%      No      fail)

:: 20. DELETE /users/:id
if defined ADMIN_TOKEN if defined MEMBER_USER_ID (
  curl -s -o "%RES%" -w "%%{http_code}" -X DELETE "%API%/users/%MEMBER_USER_ID%" -H "Authorization: Bearer %ADMIN_TOKEN%" 1>"%STATUS_FILE%"
  set /p S=<"%STATUS_FILE%"
  if %S%==200 (echo DELETE /users/:id deactivate              %S%      Yes     ok) else (echo DELETE /users/:id deactivate              %S%      No      fail)
) else (
  echo DELETE /users/:id deactivate              skip    -      no member id
)

echo ========================================
echo Done. Ensure server is running: uvicorn app.main:app --reload
endlocal
