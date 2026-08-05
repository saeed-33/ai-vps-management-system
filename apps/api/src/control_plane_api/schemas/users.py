from pydantic import BaseModel


class UserSummary(BaseModel):
    id: str
    email: str
    display_name: str
    status: str
    roles: list[str]
    source: str


class UsersListResponse(BaseModel):
    users: list[UserSummary]


class RoleSummary(BaseModel):
    code: str
    name: str
    permission_count: int


class RolesListResponse(BaseModel):
    roles: list[RoleSummary]
