"""One-time seed: create SUPER_ADMIN user if none exists. Run: python seed.py"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.core.security import hash_password
from app.database import connect_db, get_database, close_db
from app.models.user import UserDocument, UserRole
from app.repositories.user import UserRepository


async def main():
    email = (settings.super_admin_email or "").strip().lower()
    password = (settings.super_admin_password or "").strip()
    if not email or not password:
        print("Set SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASSWORD in .env")
        return 1
    await connect_db()
    db = await get_database()
    repo = UserRepository(db)
    existing = await repo.get_by_email(email)
    if existing:
        print(f"Super Admin already exists: {email}")
        await close_db()
        return 0
    doc = UserDocument(
        first_name="Super",
        last_name="Admin",
        email=email,
        hashed_password=hash_password(password),
        role=UserRole.SUPER_ADMIN,
        organization_id=None,
        language="en",
    )
    user = await repo.insert(doc)
    print(f"Super Admin created: {email} (id={user['id']})")
    await close_db()
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
