"""Organization service: create, list, get, update."""

from app.models.organization import OrganizationDocument
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository


class OrgService:
    def __init__(self, org_repo: OrganizationRepository, user_repo: UserRepository):
        self.org_repo = org_repo
        self.user_repo = user_repo

    async def create(self, name: str, created_by: str) -> dict:
        doc = OrganizationDocument(name=name, created_by=created_by)
        return await self.org_repo.insert(doc)

    async def list_all(self) -> list[dict]:
        orgs = await self.org_repo.list_all()
        for o in orgs:
            oid = o.get("id")
            if oid:
                o["member_count"] = await self.user_repo.count_by_organization(oid)
        return orgs

    async def get(self, org_id: str) -> dict | None:
        return await self.org_repo.get_by_id(org_id)

    async def update(self, org_id: str, name: str | None = None, is_active: bool | None = None) -> dict | None:
        update = {}
        if name is not None:
            update["name"] = name
        if is_active is not None:
            update["is_active"] = is_active
        if not update:
            return await self.org_repo.get_by_id(org_id)
        return await self.org_repo.update(org_id, update)
