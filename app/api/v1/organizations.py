"""Organization CRUD: SUPER_ADMIN creates/lists; ADMIN gets/updates own org."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user, get_invitation_repository, get_organization_repository, get_user_repository, require_roles, user_to_org_id
from app.models.constants import ROLE_ADMIN, ROLE_SUPER_ADMIN
from app.repositories.invitation import InvitationRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.services.org_service import OrgService
from app.services.user_service import UserService

router = APIRouter()


def get_org_service(
    org_repo: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> OrgService:
    return OrgService(org_repo, user_repo)


def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    org_repo: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    inv_repo: Annotated[InvitationRepository, Depends(get_invitation_repository)],
) -> UserService:
    return UserService(user_repo, org_repo, inv_repo)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_organization(
    body: OrganizationCreate,
    current_user: Annotated[dict, Depends(require_roles([ROLE_SUPER_ADMIN]))],
    service: Annotated[OrgService, Depends(get_org_service)],
):
    """Create organization. SUPER_ADMIN only."""
    org = await service.create(body.name, created_by=current_user["id"])
    return org


@router.get("")
async def list_organizations(
    current_user: Annotated[dict, Depends(require_roles([ROLE_SUPER_ADMIN]))],
    service: Annotated[OrgService, Depends(get_org_service)],
):
    """List all organizations. SUPER_ADMIN only."""
    return await service.list_all()


@router.get("/{org_id}/members")
async def list_organization_members(
    org_id: str,
    current_user: Annotated[dict, Depends(require_roles([ROLE_SUPER_ADMIN, ROLE_ADMIN]))],
    service: Annotated[UserService, Depends(get_user_service)],
):
    """List all team members for an organization. SUPER_ADMIN: any org; ADMIN: own org only. Use in Super Admin panel (per-org members) and Admin panel (own org)."""
    role = (current_user.get("role") or "").upper()
    if role == ROLE_ADMIN:
        if user_to_org_id(current_user) != org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your organization")
    org = await service.org_repo.get_by_id(org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return await service.list_for_org(org_id)


@router.get("/{org_id}")
async def get_organization(
    org_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[OrgService, Depends(get_org_service)],
):
    """Get one organization. SUPER_ADMIN: any; ADMIN: own org only."""
    role = (current_user.get("role") or "").upper()
    if role == ROLE_SUPER_ADMIN:
        pass
    elif role == ROLE_ADMIN:
        if user_to_org_id(current_user) != org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your organization")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    org = await service.get(org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org


@router.put("/{org_id}")
async def update_organization(
    org_id: str,
    body: OrganizationUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    service: Annotated[OrgService, Depends(get_org_service)],
):
    """Update organization. SUPER_ADMIN: any; ADMIN: own org only."""
    role = (current_user.get("role") or "").upper()
    if role == ROLE_SUPER_ADMIN:
        pass
    elif role == ROLE_ADMIN:
        if user_to_org_id(current_user) != org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your organization")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    org = await service.update(org_id, name=body.name, is_active=body.is_active)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org
