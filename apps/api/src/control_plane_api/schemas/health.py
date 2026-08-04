from pydantic import BaseModel


class ComponentStatus(BaseModel):
    name: str
    ok: bool
    detail: str


class LivenessResponse(BaseModel):
    service: str
    environment: str
    status: str


class ReadinessResponse(BaseModel):
    service: str
    environment: str
    ready: bool
    components: list[ComponentStatus]
