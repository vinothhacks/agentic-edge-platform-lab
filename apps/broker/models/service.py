from datetime import UTC, datetime
from enum import StrEnum
from typing import Optional

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


class OperationState(StrEnum):
    PENDING = "pending"
    VALIDATING = "validating"
    RENDERING = "rendering"
    APPLYING = "applying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ServicePlan(SQLModel, table=True):
    __tablename__ = "service_plans"
    id: str = Field(primary_key=True, default="edge-route-basic")
    name: str = Field(default="Edge Route - Basic")
    description: str = Field(default="Public edge route with optional auth and rate limiting")
    max_rate_limit: int = Field(default=1000)


class ServiceInstance(SQLModel, table=True):
    __tablename__ = "service_instances"
    id: Optional[int] = Field(default=None, primary_key=True)
    instance_id: str = Field(unique=True, index=True)
    name: str
    domain: str
    upstream_url: str
    auth_required: bool = False
    rate_limit: str = "100/min"
    plan_id: str = "edge-route-basic"
    state: str = "provisioned"
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class ProvisioningOperation(SQLModel, table=True):
    __tablename__ = "provisioning_operations"
    id: Optional[int] = Field(default=None, primary_key=True)
    operation_id: str = Field(unique=True, index=True)
    instance_id: str = Field(index=True)
    state: OperationState = Field(default=OperationState.PENDING)
    description: str = ""
    started_at: datetime = Field(default_factory=_utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
