"""MongoDB connection and database access."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def get_database() -> AsyncIOMotorDatabase:
    """Return the application database. Use in FastAPI Depends."""
    global _db
    if _db is None:
        await connect_db()
    return _db


async def connect_db() -> None:
    """Connect to MongoDB. Call on startup."""
    global _client, _db
    _client = AsyncIOMotorClient(
        settings.mongodb_url,
        maxPoolSize=50,
        minPoolSize=10,
        serverSelectionTimeoutMS=5000,
    )
    _db = _client[settings.mongodb_db_name]
    # Verify connection
    await _client.admin.command("ping")


async def close_db() -> None:
    """Close MongoDB connection. Call on shutdown."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
