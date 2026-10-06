from enum import StrEnum


class OrganizationRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    AGENT = "agent"
    VIEWER = "viewer"


class ClientStatus(StrEnum):
    ONBOARDING = "onboarding"
    ACTIVE = "active"
    NEEDS_ATTENTION = "needs_attention"
    DISABLED = "disabled"
