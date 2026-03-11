"""Auth service: register, login, tokens, profile."""

import logging
dbg = logging.getLogger("auth_debug")

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_access_token_expiry_seconds,
    hash_password,
    verify_password,
)
from app.repositories.user import UserRepository
from app.schemas.auth import (
    LoginResponse,
    UserCreate,
    UserProfile,
    UserProfileUpdate,
)
from app.models.user import OAuthProviderLink, UserDocument, UserRole


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, data: UserCreate) -> tuple[dict, LoginResponse]:
        dbg.debug("[service] register called")
        dbg.debug(f"[service] data.password type={type(data.password)}, value={repr(data.password)}")
        email = data.email.lower().strip()
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")
        user_doc = UserDocument(
            first_name=data.first_name,
            last_name=data.last_name,
            email=email,
            hashed_password=hash_password(data.password),
            role=data.role,
            language=data.language,
        )
        user = await self.user_repo.insert(user_doc)
        tokens = self._tokens_for_user(user["id"], user["email"])
        return user, tokens

    async def login(self, email: str, password: str) -> LoginResponse:
        email = email.lower().strip()
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")
        if not user.get("is_active", True):
            raise ValueError("Account is disabled")
        hashed = user.get("hashed_password")
        if not hashed or not verify_password(password, hashed):
            raise ValueError("Invalid email or password")
        await self.user_repo.set_last_login(user["id"])
        return self._tokens_for_user(user["id"], user["email"])

    def _tokens_for_user(self, user_id: str, email: str) -> LoginResponse:
        access = create_access_token(sub=user_id, email=email)
        refresh = create_refresh_token(sub=user_id, email=email)
        return LoginResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=get_access_token_expiry_seconds(),
        )

    async def refresh_tokens(self, refresh_token: str) -> LoginResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        sub = payload.get("sub")
        if not sub:
            raise ValueError("Invalid refresh token")
        user = await self.user_repo.get_by_id(sub)
        if not user or not user.get("is_active", True):
            raise ValueError("User not found or disabled")
        return self._tokens_for_user(user["id"], user["email"])

    def user_to_profile(self, user: dict) -> UserProfile:
        return UserProfile(
            id=user["id"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            role=UserRole(user.get("role", "client")),
            profile_picture=user.get("profile_picture"),
            language=user.get("language", "en"),
            timezone=user.get("timezone"),
            email_verified=user.get("email_verified", False),
            is_active=user.get("is_active", True),
            organization_ids=user.get("organization_ids", []),
            created_at=user.get("created_at", ""),
            last_login_at=user.get("last_login_at"),
        )

    async def update_profile(self, user_id: str, data: UserProfileUpdate) -> dict:
        update = data.model_dump(exclude_unset=True)
        if not update:
            user = await self.user_repo.get_by_id(user_id)
            return user or {}
        return await self.user_repo.update(user_id, update) or {}

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        hashed = user.get("hashed_password")
        if not hashed or not verify_password(current_password, hashed):
            raise ValueError("Current password is incorrect")
        from app.core.security import hash_password
        await self.user_repo.update(user_id, {"hashed_password": hash_password(new_password)})

    async def google_oauth_login(
        self,
        google_id: str,
        email: str,
        given_name: str,
        family_name: str,
        picture: str | None = None,
    ) -> LoginResponse:
        """Find or create user from Google OAuth and return tokens."""
        email = email.lower().strip() if email else ""
        if not email:
            raise ValueError("Google account has no email")
        # Existing user linked to this Google account
        user = await self.user_repo.get_by_oauth("google", google_id)
        if user:
            if not user.get("is_active", True):
                raise ValueError("Account is disabled")
            await self.user_repo.set_last_login(user["id"])
            return self._tokens_for_user(user["id"], user["email"])
        # Existing user with same email: link Google
        user = await self.user_repo.get_by_email(email)
        if user:
            await self.user_repo.add_oauth_provider(user["id"], "google", google_id)
            if not user.get("is_active", True):
                raise ValueError("Account is disabled")
            await self.user_repo.set_last_login(user["id"])
            return self._tokens_for_user(user["id"], user["email"])
        # New user
        user_doc = UserDocument(
            first_name=given_name or "User",
            last_name=family_name or "",
            email=email,
            hashed_password=None,
            role=UserRole.CLIENT,
            profile_picture=picture,
            language="en",
            email_verified=True,
            oauth_providers=[OAuthProviderLink(provider="google", provider_user_id=google_id)],
        )
        user = await self.user_repo.insert(user_doc)
        return self._tokens_for_user(user["id"], user["email"])
