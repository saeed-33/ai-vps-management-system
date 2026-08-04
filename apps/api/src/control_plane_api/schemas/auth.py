from pydantic import BaseModel


class TokenRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class Principal(BaseModel):
    subject: str
    email: str
    display_name: str
    roles: list[str]
    permissions: list[str]


class PermissionDefinition(BaseModel):
    code: str
    description: str


class RoleDefinition(BaseModel):
    code: str
    name: str
    permissions: list[str]


class RbacCatalog(BaseModel):
    roles: list[RoleDefinition]
    permissions: list[PermissionDefinition]
