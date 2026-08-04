from pydantic import BaseModel


class ModuleStatus(BaseModel):
    name: str
    status: str


class ServiceMetadata(BaseModel):
    service: str
    environment: str
    version: str
    api_prefix: str
    modules: list[ModuleStatus]
