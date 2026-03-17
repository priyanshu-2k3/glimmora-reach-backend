"""FastAPI dependencies: auth, DB, RBAC."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import decode_token
from app.database import get_database
from app.models.constants import role_to_response
from app.repositories.invitation import InvitationRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository


async def get_user_repository(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> UserRepository:
    return UserRepository(db)


async def get_organization_repository(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> OrganizationRepository:
    return OrganizationRepository(db)


async def get_invitation_repository(
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> InvitationRepository:
    return InvitationRepository(db)


security_bearer = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_bearer)],
) -> str:
    if not credentials or credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return sub


async def get_current_user(
    user_id: Annotated[str, Depends(get_current_user_id)],
    repo: Annotated[UserRepository, Depends(get_user_repository)],
):
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled",
        )
    return user


def require_roles(allowed_roles: list[str]):
    """Dependency factory: require current user to have one of allowed_roles (uppercase)."""

    async def _require(
        user: Annotated[dict, Depends(get_current_user)],
    ) -> dict:
        role = (user.get("role") or "").upper()
        if role not in [r.upper() for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _require


def user_to_org_id(user: dict) -> str | None:
    """Get organization id for API response (orgId)."""
    oid = user.get("organization_id")
    if oid:
        return oid
    ids = user.get("organization_ids") or []
    return ids[0] if ids else None
