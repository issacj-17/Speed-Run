"""
Integration test fixtures.

Provides real database and cache for integration testing.
"""

import pytest
import asyncio
from pathlib import Path
from typing import AsyncGenerator
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.models import Base, Alert, Client, Document
from backend.schemas.alert import AlertCreate, AlertSeverity, AlertStatus
from backend.services.alert_service import AlertService
from backend.services.corroboration_service import CorroborationService
from backend.container import get_container, Container


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture(scope="function")
async def integration_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide real test database session for integration tests.

    Uses in-memory SQLite with all tables created.

    Usage:
        async def test_something(integration_db):
            service = AlertService(integration_db)
            ...

    Yields:
        AsyncSession: Database session
    """
    # Create in-memory SQLite database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL debugging
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# ============================================================================
# Service Fixtures
# ============================================================================


@pytest.fixture
def alert_service_integration(integration_db) -> AlertService:
    """
    Provide AlertService with real database session.

    Usage:
        async def test_something(alert_service_integration):
            alert = await alert_service_integration.create_alert(...)
    """
    return AlertService(db=integration_db)


@pytest.fixture
def container_integration() -> Container:
    """
    Provide DI container with real adapters.

    Usage:
        async def test_something(container_integration):
            parser = container_integration.document_parser
            result = await parser.parse(...)
    """
    return get_container()


@pytest.fixture
def corroboration_service_integration(container_integration) -> CorroborationService:
    """
    Provide CorroborationService with real adapters.

    Usage:
        async def test_something(corroboration_service_integration):
            result = await corroboration_service_integration.analyze_document(...)
    """
    return CorroborationService(
        document_parser=container_integration.document_parser,
        nlp_processor=container_integration.nlp_processor,
        image_processor=container_integration.image_processor,
    )


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
async def client_in_db(integration_db) -> Client:
    """
    Create test client in database.

    Returns:
        Client: Test client entity
    """
    client = Client(
        id=uuid4(),
        name="Test Client",
        email="test@example.com",
        phone="555-1234",
        kyc_status="PENDING",
        risk_level="MEDIUM",
    )

    integration_db.add(client)
    await integration_db.commit()
    await integration_db.refresh(client)

    return client


@pytest.fixture
async def document_in_db(integration_db, client_in_db) -> Document:
    """
    Create test document in database.

    Returns:
        Document: Test document entity
    """
    document = Document(
        id=uuid4(),
        client_id=client_in_db.id,
        file_name="test_document.pdf",
        file_path="/tmp/test_document.pdf",
        file_type="application/pdf",
        file_size=1024,
        upload_status="UPLOADED",
    )

    integration_db.add(document)
    await integration_db.commit()
    await integration_db.refresh(document)

    return document


@pytest.fixture
async def alert_in_db(integration_db, client_in_db) -> Alert:
    """
    Create test alert in database.

    Returns:
        Alert: Test alert entity
    """
    alert = Alert(
        id=uuid4(),
        alert_type="TRANSACTION_RISK",
        severity=AlertSeverity.MEDIUM,
        status=AlertStatus.NEW,
        client_id=client_in_db.id,
        title="Test Alert",
        description="Integration test alert",
        risk_score=50,
        triggered_rules={"rule1": True},
        context={"test": True},
        recommended_actions=["Review"],
    )

    integration_db.add(alert)
    await integration_db.commit()
    await integration_db.refresh(alert)

    return alert


@pytest.fixture
async def multiple_alerts_in_db(integration_db, client_in_db) -> list[Alert]:
    """
    Create multiple test alerts in database.

    Returns:
        list[Alert]: List of test alerts
    """
    alerts = []

    for i in range(5):
        alert = Alert(
            id=uuid4(),
            alert_type="TRANSACTION_RISK",
            severity=AlertSeverity.MEDIUM if i % 2 == 0 else AlertSeverity.HIGH,
            status=AlertStatus.NEW if i < 3 else AlertStatus.ACKNOWLEDGED,
            client_id=client_in_db.id,
            title=f"Test Alert {i}",
            description=f"Integration test alert {i}",
            risk_score=50 + i * 10,
            triggered_rules={"rule1": True},
            context={"test": True, "index": i},
            recommended_actions=["Review"],
        )
        integration_db.add(alert)
        alerts.append(alert)

    await integration_db.commit()

    for alert in alerts:
        await integration_db.refresh(alert)

    return alerts


# ============================================================================
# Test File Fixtures
# ============================================================================


@pytest.fixture
def integration_temp_pdf(tmp_path) -> Path:
    """
    Create temporary PDF file for integration tests.

    Args:
        tmp_path: pytest's temporary directory fixture

    Returns:
        Path: Path to temporary PDF file
    """
    pdf_path = tmp_path / "test_integration.pdf"
    pdf_path.write_bytes(b'%PDF-1.4\n%Integration Test PDF\n%%EOF\n')
    return pdf_path


@pytest.fixture
def integration_temp_image(tmp_path) -> Path:
    """
    Create temporary image file for integration tests.

    Args:
        tmp_path: pytest's temporary directory fixture

    Returns:
        Path: Path to temporary image file
    """
    from PIL import Image
    import numpy as np

    image_path = tmp_path / "test_integration.jpg"

    # Create test image
    img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(img_array, mode='RGB')
    img.save(image_path, format='JPEG')

    return image_path


# ============================================================================
# Data Builder Functions
# ============================================================================


def build_alert_create_integration(client_id, **overrides) -> AlertCreate:
    """
    Build AlertCreate for integration tests.

    Args:
        client_id: Client UUID
        **overrides: Fields to override

    Returns:
        AlertCreate: Alert creation data
    """
    defaults = {
        "alert_type": "TRANSACTION_RISK",
        "severity": AlertSeverity.MEDIUM,
        "client_id": client_id,
        "transaction_id": uuid4(),
        "document_id": None,
        "title": "Integration Test Alert",
        "description": "Created during integration testing",
        "risk_score": 50,
        "triggered_rules": {"rule1": True},
        "context": {"integration_test": True},
        "recommended_actions": ["Review manually"],
    }
    defaults.update(overrides)
    return AlertCreate(**defaults)


__all__ = [
    "integration_db",
    "alert_service_integration",
    "container_integration",
    "corroboration_service_integration",
    "client_in_db",
    "document_in_db",
    "alert_in_db",
    "multiple_alerts_in_db",
    "integration_temp_pdf",
    "integration_temp_image",
    "build_alert_create_integration",
]
