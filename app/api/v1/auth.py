"""Auth routes: register, login, profile, change password, Google OAuth."""

import urllib.parse
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr

from app.config import settings
from app.core.deps import get_current_user, get_current_user_id, get_user_repository
from app.repositories.user import UserRepository
from app.schemas.auth import (
    ChangePasswordBody,
    LoginResponse,
    UserCreate,
    UserProfile,
    UserProfileUpdate,
)
from app.schemas.common import MessageResponse
from app.services.auth import AuthService
from app.services.oauth_google import (
    exchange_code_for_tokens,
    get_google_authorize_url,
    get_google_user_info,
)


def get_auth_service(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(repo)


router = APIRouter()


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class RefreshBody(BaseModel):
    refresh_token: str


@router.post("/register", response_model=LoginResponse)
async def register(
    body: UserCreate,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    """Register a new user. Returns tokens."""
    try:
        import logging; dbg = logging.getLogger("auth_debug")
        dbg.debug(f"[route] register body.password type={type(body.password)}, value={repr(body.password)}")
        _, tokens = await service.register(body)
        return tokens
    except ValueError as e:
        if "already registered" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginBody,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    """Login with email and password."""
    try:
        return await service.login(body.email, body.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/refresh", response_model=LoginResponse)
async def refresh(
    body: RefreshBody,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    """Issue new access and refresh tokens using a valid refresh token."""
    try:
        return await service.refresh_tokens(body.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get("/me", response_model=UserProfile)
async def get_profile(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserProfile:
    """Get current user profile. Requires Bearer token."""
    return service.user_to_profile(current_user)


@router.patch("/me", response_model=UserProfile)
async def patch_profile(
    body: UserProfileUpdate,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserProfile:
    """Update current user profile (partial)."""
    updated = await service.update_profile(current_user_id, body)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return service.user_to_profile(updated)


@router.delete("/me", response_model=MessageResponse)
async def delete_profile(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> MessageResponse:
    """Delete current user account."""
    ok = await repo.delete(current_user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return MessageResponse(message="Account deleted")


@router.post("/me/change-password", response_model=MessageResponse)
async def change_password(
    body: ChangePasswordBody,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    """Change password for current user."""
    try:
        await service.change_password(
            current_user_id,
            body.current_password,
            body.new_password,
        )
        return MessageResponse(message="Password updated")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ----- Google OAuth -----


@router.get("/oauth/google")
async def oauth_google_start(
    state: str | None = Query(None, description="Optional state to pass back to frontend"),
) -> RedirectResponse:
    """Redirect user to Google consent screen. After login, Google redirects to /oauth/google/callback."""
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )
    url = get_google_authorize_url(state=state)
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@router.get("/oauth/google/callback", response_model=LoginResponse)
async def oauth_google_callback(
    service: Annotated[AuthService, Depends(get_auth_service)],
    code: str = Query(..., description="Authorization code from Google"),
    redirect: bool = Query(True, description="If true, redirect to frontend with tokens in fragment"),
) -> LoginResponse | RedirectResponse:
    """Exchange Google code for user and return tokens. If redirect=true, redirects to frontend with tokens in URL fragment."""
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )
    try:
        tokens = await exchange_code_for_tokens(code)
        access_token = tokens.get("access_token")
        if not access_token:
            raise ValueError("No access token from Google")
        user_info = await get_google_user_info(access_token)
        google_id = str(user_info.get("id", ""))
        email = user_info.get("email") or ""
        given_name = user_info.get("given_name") or ""
        family_name = user_info.get("family_name") or ""
        picture = user_info.get("picture")
        login_response = await service.google_oauth_login(
            google_id=google_id,
            email=email,
            given_name=given_name,
            family_name=family_name,
            picture=picture,
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google OAuth failed",
        ) from e

    if redirect and settings.frontend_oauth_redirect_uri:
        fragment = urllib.parse.urlencode({
            "access_token": login_response.access_token,
            "refresh_token": login_response.refresh_token,
            "expires_in": str(login_response.expires_in),
            "token_type": login_response.token_type,
        })
        return RedirectResponse(
            url=f"{settings.frontend_oauth_redirect_uri}#{fragment}",
            status_code=status.HTTP_302_FOUND,
        )
    return login_response
