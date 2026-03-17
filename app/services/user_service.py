"""User management: create-admin, invite, list, update role, deactivate."""

import secrets
from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.models.constants import (
    ROLE_ADMIN,
    ROLE_SUPER_ADMIN,
    response_role_to_db,
    role_to_response,
)
from app.models.invitation import InvitationDocument
from app.models.user import UserDocument, UserRole
from app.repositories.invitation import InvitationRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        org_repo: OrganizationRepository,
        inv_repo: InvitationRepository,
    ):
        self.user_repo = user_repo
        self.org_repo = org_repo
        self.inv_repo = inv_repo

    async def create_admin(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        organization_id: str,
    ) -> dict:
        org = await self.org_repo.get_by_id(organization_id)
        if not org:
            raise ValueError("Organization not found")
        email = email.lower().strip()
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")
        user_doc = UserDocument(
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
            organization_id=organization_id,
        )
        return await self.user_repo.insert(user_doc)

    async def invite(self, email: str, role: str, organization_id: str, invited_by: str) -> dict:
        email = email.lower().strip()
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=72)
        inv = InvitationDocument(
            email=email,
            role=role,
            organization_id=organization_id,
            invited_by=invited_by,
            token=token,
            status="PENDING",
            expires_at=expires_at,
        )
        return await self.inv_repo.insert(inv)

    def _user_to_list_item(self, user: dict) -> dict:
        name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get("email", "")
        return {
            "id": user["id"],
            "name": name,
            "email": user["email"],
            "role": role_to_response(user.get("role", "")),
            "is_active": user.get("is_active", True),
            "created_at": user.get("created_at", ""),
        }

    async def list_for_org(self, organization_id: str) -> list[dict]:
        users = await self.user_repo.list_by_organization(organization_id)
        return [self._user_to_list_item(u) for u in users]

    async def list_all_super_admin(self) -> list[dict]:
        users = await self.user_repo.list_all_for_super_admin()
        return [self._user_to_list_item(u) for u in users]

    async def update_role(
        self,
        user_id: str,
        new_role: str,
        admin_org_id: str | None,
        is_super_admin: bool = False,
    ) -> dict | None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        if admin_org_id:
            target_org = user.get("organization_id") or (user.get("organization_ids") or [None])[0]
            if target_org != admin_org_id:
                return None
        role_db = response_role_to_db(new_role)
        if role_db == ROLE_SUPER_ADMIN:
            return None
        if not is_super_admin and role_db == ROLE_ADMIN:
            return None
        return await self.user_repo.update_role(user_id, role_db)

    async def deactivate(self, user_id: str, admin_org_id: str | None) -> bool:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return False
        if admin_org_id:
            target_org = user.get("organization_id") or (user.get("organization_ids") or [None])[0]
            if target_org != admin_org_id:
                return False
        result = await self.user_repo.set_active(user_id, False)
        return result is not None
