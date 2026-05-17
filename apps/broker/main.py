"""Broker API — OSB-compatible endpoints + platform /api/* endpoints."""
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from .api.agent import router as agent_router
from .core.db import get_session, init_db
from .models.service import (
    OperationState,
    ProvisioningOperation,
    ServiceInstance,
    ServicePlan,
)
from .schemas.service import (
    CatalogResponse,
    OperationRead,
    ServiceCreate,
    ServiceRead,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Agentic Edge Platform Lab — Broker",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(agent_router)


@app.get("/v2/catalog", response_model=CatalogResponse)
def get_catalog(session: Session = Depends(get_session)):
    plans = session.exec(select(ServicePlan)).all()
    if not plans:
        plan = ServicePlan()
        session.add(plan)
        session.commit()
        session.refresh(plan)
        plans = [plan]
    return {
        "services": [
            {
                "id": "edge-route",
                "name": "Edge Route",
                "description": "Public edge route with optional auth and rate-limiting",
                "plans": [{"id": p.id, "name": p.name} for p in plans],
            }
        ],
        "plans": [{"id": p.id, "name": p.name, "description": p.description} for p in plans],
    }


@app.get("/v2/service_instances/{instance_id}/last_operation", response_model=OperationRead)
def last_operation(instance_id: str, session: Session = Depends(get_session)):
    op = session.exec(
        select(ProvisioningOperation)
        .where(ProvisioningOperation.instance_id == instance_id)
        .order_by(ProvisioningOperation.started_at.desc())  # type: ignore[arg-type]
    ).first()
    if not op:
        raise HTTPException(404, "No operation found for this instance")
    return OperationRead(
        operation_id=op.operation_id,
        instance_id=op.instance_id,
        state=op.state.value,
        description=op.description,
        started_at=op.started_at,
        completed_at=op.completed_at,
        error_message=op.error_message,
    )


@app.post("/api/services", response_model=ServiceRead, status_code=201)
def create_service(payload: ServiceCreate, session: Session = Depends(get_session)):
    instance_id = str(uuid4())
    svc = ServiceInstance(
        instance_id=instance_id,
        name=payload.name,
        domain=payload.domain,
        upstream_url=payload.upstream_url,
        auth_required=payload.auth_required,
        rate_limit=payload.rate_limit,
    )
    session.add(svc)
    session.commit()
    session.refresh(svc)

    op = ProvisioningOperation(
        operation_id=str(uuid4()),
        instance_id=instance_id,
        state=OperationState.PENDING,
        description="Provisioning requested",
    )
    session.add(op)
    session.commit()

    return ServiceRead(
        instance_id=svc.instance_id,
        name=svc.name,
        domain=svc.domain,
        upstream_url=svc.upstream_url,
        auth_required=svc.auth_required,
        rate_limit=svc.rate_limit,
        state=svc.state,
        created_at=svc.created_at,
    )


@app.get("/api/services", response_model=list[ServiceRead])
def list_services(session: Session = Depends(get_session)):
    svcs = session.exec(select(ServiceInstance)).all()
    return [
        ServiceRead(
            instance_id=s.instance_id,
            name=s.name,
            domain=s.domain,
            upstream_url=s.upstream_url,
            auth_required=s.auth_required,
            rate_limit=s.rate_limit,
            state=s.state,
            created_at=s.created_at,
        )
        for s in svcs
    ]


@app.get("/api/services/{instance_id}", response_model=ServiceRead)
def get_service(instance_id: str, session: Session = Depends(get_session)):
    svc = session.exec(
        select(ServiceInstance).where(ServiceInstance.instance_id == instance_id)
    ).first()
    if not svc:
        raise HTTPException(404, "Service not found")
    return ServiceRead(
        instance_id=svc.instance_id,
        name=svc.name,
        domain=svc.domain,
        upstream_url=svc.upstream_url,
        auth_required=svc.auth_required,
        rate_limit=svc.rate_limit,
        state=svc.state,
        created_at=svc.created_at,
    )


@app.get("/healthz")
def health():
    return {"status": "ok"}
