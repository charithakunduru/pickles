import enum

class UserRole(str, enum.Enum):
    ROLE_USER = "roleuser"
    ROLE_ADMIN = "roleadmin"
