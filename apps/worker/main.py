"""Async Worker - Phase 2: processes provisioning jobs with state machine."""
import asyncio
from datetime import UTC, datetime

from sqlmodel import Session, select

from apps.broker.core.db import engine
from apps.broker.models.service import (
    OperationState,
    ProvisioningOperation,
    ServiceInstance,
)
from apps.broker.services.config_renderer import ConfigRenderer


async def run_worker():
    print("Worker started (in-memory + DB polling mode)")
    renderer = ConfigRenderer()
    while True:
        with Session(engine) as session:
            pending_ops = session.exec(
                select(ProvisioningOperation).where(
                    ProvisioningOperation.state == OperationState.PENDING
                )
            ).all()
            for op in pending_ops:
                op.state = OperationState.VALIDATING
                op.description = "Validating request..."
                session.add(op)
                session.commit()

                svc = session.exec(
                    select(ServiceInstance).where(
                        ServiceInstance.instance_id == op.instance_id
                    )
                ).first()
                if not svc:
                    op.state = OperationState.FAILED
                    op.error_message = "Service instance not found"
                elif "localhost" not in svc.domain:
                    op.state = OperationState.FAILED
                    op.error_message = "Invalid domain (must end in .localhost in this lab)"
                else:
                    op.state = OperationState.RENDERING
                    op.description = "Rendering Envoy config..."
                    session.add(op)
                    session.commit()

                    result = renderer.render(svc)
                    if not result.success:
                        op.state = OperationState.FAILED
                        op.error_message = f"Render failed: {result.error}"
                    else:
                        op.state = OperationState.SUCCEEDED
                        op.description = (
                            f"Route provisioned; config at {result.config_path}"
                        )
                        op.completed_at = datetime.now(UTC)

                session.add(op)
                session.commit()
                print(f"Operation {op.operation_id} -> {op.state}")

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(run_worker())
