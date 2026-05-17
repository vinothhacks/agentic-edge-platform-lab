"""Test configuration: shared in-memory SQLite so all sessions see the same tables."""
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

import apps.broker.core.db as db_module

# StaticPool keeps a single connection alive -- critical for in-memory SQLite
_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Patch the module-level engine before any import uses it, then create tables."""
    db_module.engine = _test_engine
    SQLModel.metadata.create_all(_test_engine)
    yield
    SQLModel.metadata.drop_all(_test_engine)
