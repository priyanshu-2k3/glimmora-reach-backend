"""Auth service: register, login, tokens, profile, accept-invite."""

import logging
dbg = logging.getLogger("auth_debug")

from app.core.deps import user_to_org_id
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_access_token_expiry_seconds,
    hash_password,
    verify_password,
)
from app.models.constants import db_role_to_enum_value, role_to_response
from app.models.user import OAuthProviderLink, UserDocument, UserRole
from app.repositories.invitation import InvitationRepository
from app.repositories.user import UserRepository
from app.schemas.auth import (
    AcceptInviteBody,
    LoginResponse,
    UserCreate,
    UserLoginShape,
    UserProfile,
    UserProfileUpdate,
)


class AuthService:
    def __init__(self, user_repo: UserRepository, invitation_repo: InvitationRepository | None = None):
        self.user_repo = user_repo
        self.invitation_repo = invitation_repo or None

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
        return user, self._tokens_for_user(user, include_user=True)

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
        return self._tokens_for_user(user, include_user=True)

    def _user_to_login_shape(self, user: dict) -> UserLoginShape:
        name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get("email", "")
        return UserLoginShape(
            id=user["id"],
            name=name,
            email=user["email"],
            role=role_to_response(user.get("role", "")),
            orgId=user_to_org_id(user),
            avatar=user.get("profile_picture"),
            createdAt=user.get("created_at", ""),
        )

    def _tokens_for_user(self, user: dict, include_user: bool = False) -> LoginResponse:
        user_id = user["id"]
        email = user.get("email", "")
        role = (user.get("role") or "").upper()
        org_id = user_to_org_id(user)
        access = create_access_token(sub=user_id, email=email, role=role, org_id=org_id)
        refresh = create_refresh_token(sub=user_id, email=email)
        out = LoginResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=get_access_token_expiry_seconds(),
        )
        if include_user:
            out.user = self._user_to_login_shape(user)
        return out

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
        return self._tokens_for_user(user, include_user=True)

    def user_to_profile(self, user: dict) -> UserProfile:
        return UserProfile(
            id=user["id"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            role=UserRole(db_role_to_enum_value(user.get("role", ""))),
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
            return self._tokens_for_user(user, include_user=True)
        # Existing user with same email: link Google
        user = await self.user_repo.get_by_email(email)
        if user:
            await self.user_repo.add_oauth_provider(user["id"], "google", google_id)
            if not user.get("is_active", True):
                raise ValueError("Account is disabled")
            await self.user_repo.set_last_login(user["id"])
            return self._tokens_for_user(user, include_user=True)
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
        return self._tokens_for_user(user, include_user=True)

    async def accept_invite(self, data: AcceptInviteBody) -> LoginResponse:
        if not self.invitation_repo:
            raise ValueError("Invitations not configured")
        inv = await self.invitation_repo.get_by_token(data.token)
        if not inv:
            raise ValueError("Invalid or expired invite token")
        if inv.get("status") != "PENDING":
            raise ValueError("Invitation already used or expired")
        from datetime import datetime, timezone
        exp = inv.get("expires_at")
        if exp and isinstance(exp, str):
            try:
                exp_dt = datetime.fromisoformat(exp.replace("Z", "+00:00"))
            except Exception:
                exp_dt = None
        else:
            exp_dt = exp
        if exp_dt and exp_dt < datetime.now(timezone.utc):
            await self.invitation_repo.update_status(inv["id"], "EXPIRED")
            raise ValueError("Invitation has expired")
        email = (inv.get("email") or "").lower().strip()
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")
        org_id = inv.get("organization_id")
        role_db = inv.get("role", "VIEWER")
        user_doc = UserDocument(
            first_name=data.first_name,
            last_name=data.last_name,
            email=email,
            hashed_password=hash_password(data.password),
            role=UserRole(db_role_to_enum_value(role_db)),
            language="en",
            organization_id=org_id,
        )
        user = await self.user_repo.insert(user_doc)
        await self.invitation_repo.set_accepted(data.token)
        return self._tokens_for_user(user, include_user=True)
