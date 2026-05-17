from datetime import UTC, datetime

from sqlmodel import Session, select

import apps.broker.core.db as db_module
from apps.broker.models.service import (
    OperationState,
    ProvisioningOperation,
    ServiceInstance,
)


def test_operation_state_transitions():
    """Verify pending -> succeeded state transition persists correctly."""
    with Session(db_module.engine) as session:
        instance_id = "state-test-inst-001"
        svc = ServiceInstance(
            instance_id=instance_id,
            name="state-test",
            domain="state-test.localhost",
            upstream_url="http://state-test:8080",
        )
        session.add(svc)
        session.commit()

        op = ProvisioningOperation(
            operation_id="op-state-test-001",
            instance_id=instance_id,
            state=OperationState.PENDING,
        )
        session.add(op)
        session.commit()

        op.state = OperationState.SUCCEEDED
        op.completed_at = datetime.now(UTC)
        session.add(op)
        session.commit()

        fetched = session.exec(
            select(ProvisioningOperation).where(
                ProvisioningOperation.operation_id == "op-state-test-001"
            )
        ).first()
        assert fetched is not None
        assert fetched.state == OperationState.SUCCEEDED
        assert fetched.completed_at is not None
