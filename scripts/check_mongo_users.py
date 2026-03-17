"""Check if users are stored in MongoDB. Run from project root:
   python scripts/check_mongo_users.py
"""
import asyncio
import sys
sys.path.insert(0, ".")

from app.config import settings
from app.database import connect_db, get_database, close_db


async def main():
    await connect_db()
    db = await get_database()
    coll = db["users"]
    count = await coll.count_documents({})
    print(f"Database: {settings.mongodb_db_name}")
    print(f"Collection: users")
    print(f"Total users: {count}")
    if count > 0:
        print("\nDocuments (id, email, first_name, last_name, role, created_at):")
        async for doc in coll.find({}).sort("created_at", -1).limit(20):
            uid = str(doc.get("_id", ""))
            email = doc.get("email", "")
            first = doc.get("first_name", "")
            last = doc.get("last_name", "")
            role = doc.get("role", "")
            created = doc.get("created_at", "")
            has_pw = "yes" if doc.get("hashed_password") else "no"
            print(f"  {uid[:8]}... | {email} | {first} {last} | {role} | pwd:{has_pw} | {created}")
    await close_db()


if __name__ == "__main__":
    asyncio.run(main())
