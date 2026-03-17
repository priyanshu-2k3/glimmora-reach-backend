"""Role constants: stored uppercase in DB, returned lowercase to frontend per spec."""

# Stored in MongoDB (uppercase)
ROLE_SUPER_ADMIN = "SUPER_ADMIN"
ROLE_ADMIN = "ADMIN"
ROLE_CAMPAIGN_MANAGER = "CAMPAIGN_MANAGER"
ROLE_ANALYTICS = "ANALYTICS"
ROLE_VIEWER = "VIEWER"

ROLES_ALL = (ROLE_SUPER_ADMIN, ROLE_ADMIN, ROLE_CAMPAIGN_MANAGER, ROLE_ANALYTICS, ROLE_VIEWER)

# API response (lowercase); spec Section 10: ANALYTICS->analyst, VIEWER->client
def role_to_response(role: str) -> str:
    if not role:
        return "client"
    r = role.upper()
    if r == ROLE_ANALYTICS:
        return "analyst"
    if r == ROLE_VIEWER:
        return "client"
    if r == ROLE_SUPER_ADMIN:
        return "super_admin"
    if r == ROLE_ADMIN:
        return "admin"
    if r == ROLE_CAMPAIGN_MANAGER:
        return "campaign_manager"
    return role.lower()

def response_role_to_db(role: str) -> str:
    """Map frontend role to DB role (uppercase)."""
    if not role:
        return ROLE_VIEWER
    r = role.lower()
    if r == "analyst":
        return ROLE_ANALYTICS
    if r == "client":
        return ROLE_VIEWER
    if r == "super_admin":
        return ROLE_SUPER_ADMIN
    if r == "admin":
        return ROLE_ADMIN
    if r == "campaign_manager":
        return ROLE_CAMPAIGN_MANAGER
    return role.upper()


# Map DB role (uppercase) to UserRole enum value (lowercase) for Pydantic
DB_ROLE_TO_USER_ROLE_VALUE = {
    ROLE_SUPER_ADMIN: "super_admin",
    ROLE_ADMIN: "admin",
    ROLE_CAMPAIGN_MANAGER: "campaign_manager",
    ROLE_ANALYTICS: "analyst",
    ROLE_VIEWER: "client",
}


def db_role_to_enum_value(role: str) -> str:
    return DB_ROLE_TO_USER_ROLE_VALUE.get((role or "").upper(), "client")
