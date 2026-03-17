"""User management: create-admin (SUPER_ADMIN), invite/list/role/delete (ADMIN)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user, get_invitation_repository, get_organization_repository, get_user_repository, require_roles, user_to_org_id
from app.models.constants import ROLE_ADMIN, ROLE_SUPER_ADMIN
from app.repositories.invitation import InvitationRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository
from app.schemas.common import MessageResponse
from app.schemas.user import CreateAdminBody, InviteBody, UserRoleUpdateBody
from app.services.user_service import UserService

router = APIRouter()


def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    org_repo: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    inv_repo: Annotated[InvitationRepository, Depends(get_invitation_repository)],
) -> UserService:
    return UserService(user_repo, org_repo, inv_repo)


@router.post("/create-admin", status_code=status.HTTP_201_CREATED)
async def create_admin(
    body: CreateAdminBody,
    current_user: Annotated[dict, Depends(require_roles([ROLE_SUPER_ADMIN]))],
    service: Annotated[UserService, Depends(get_user_service)],
):
    """Create an ADMIN user for an organization. SUPER_ADMIN only."""
    try:
        user = await service.create_admin(
            body.first_name,
            body.last_name,
            body.email,
            body.password,
            body.organization_id,
        )
        return {k: v for k, v in user.items() if k != "hashed_password"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/invite", status_code=status.HTTP_201_CREATED)
async def invite_user(
    body: InviteBody,
    current_user: Annotated[dict, Depends(require_roles([ROLE_ADMIN]))],
    service: Annotated[UserService, Depends(get_user_service)],
):
    """Send invite to a user. ADMIN only (own org)."""
    org_id = user_to_org_id(current_user)
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No organization")
    try:
        inv = await service.invite(
            body.email,
            body.role,
            org_id,
            current_user["id"],
        )
        return inv
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("")
async def list_users(
    current_user: Annotated[dict, Depends(require_roles([ROLE_SUPER_ADMIN, ROLE_ADMIN]))],
    service: Annotated[UserService, Depends(get_user_service)],
):
    """List users. SUPER_ADMIN: all; ADMIN: own org only."""
    role = (current_user.get("role") or "").upper()
    if role == ROLE_SUPER_ADMIN:
        return await service.list_all_super_admin()
    org_id = user_to_org_id(current_user)
    if not org_id:
        return []
    return await service.list_for_org(org_id)


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: str,
    body: UserRoleUpdateBody,
    current_user: Annotated[dict, Depends(require_roles([ROLE_ADMIN]))],
    service: Annotated[UserService, Depends(get_user_service)],
):
    """Change a user's role. ADMIN only (own org). Cannot set SUPER_ADMIN or ADMIN."""
    org_id = user_to_org_id(current_user)
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No organization")
    user = await service.update_role(user_id, body.role, admin_org_id=org_id, is_super_admin=False)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or not in your org")
    return {k: v for k, v in user.items() if k != "hashed_password"}


@router.delete("/{user_id}", response_model=MessageResponse)
async def deactivate_user(
    user_id: str,
    current_user: Annotated[dict, Depends(require_roles([ROLE_ADMIN]))],
    service: Annotated[UserService, Depends(get_user_service)],
):
    """Soft delete (deactivate) user. ADMIN only (own org)."""
    org_id = user_to_org_id(current_user)
    if not org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No organization")
    ok = await service.deactivate(user_id, admin_org_id=org_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or not in your org")
    return MessageResponse(message="User deactivated")
