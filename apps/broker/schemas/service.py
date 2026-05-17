from datetime import datetime

from pydantic import BaseModel, Field


class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-z0-9-]+$")
    domain: str = Field(..., description="Public domain, e.g. orders.localhost")
    upstream_url: str = Field(..., description="Upstream service URL inside the network")
    auth_required: bool = False
    rate_limit: str = Field(default="100/min", pattern=r"^\d+/(min|sec)$")


class ServiceRead(BaseModel):
    instance_id: str
    name: str
    domain: str
    upstream_url: str
    auth_required: bool
    rate_limit: str
    state: str
    created_at: datetime


class ServiceUpdate(BaseModel):
    auth_required: bool | None = None
    rate_limit: str | None = None


class OperationRead(BaseModel):
    operation_id: str
    instance_id: str
    state: str
    description: str
    started_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None


class CatalogResponse(BaseModel):
    services: list[dict]
    plans: list[dict]
