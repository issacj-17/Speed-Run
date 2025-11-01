"""
Unit tests for AlertService.

Tests alert management service with mocked database session.
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.alert_service import AlertService
from backend.schemas.alert import AlertCreate, AlertUpdate, AlertStatus, AlertSeverity
from backend.database.models import Alert


# ============================================================================
# Test Data Builders
# ============================================================================


def build_alert_create(**overrides) -> AlertCreate:
    """Build AlertCreate with sensible defaults."""
    defaults = {
        "alert_type": "TRANSACTION_RISK",
        "severity": AlertSeverity.MEDIUM,
        "client_id": uuid4(),
        "transaction_id": uuid4(),
        "document_id": None,
        "title": "Test alert",
        "description": "Test description",
        "risk_score": 50,
        "triggered_rules": {"rule1": True},
        "context": {"key": "value"},
        "recommended_actions": ["Review manually"],
    }
    defaults.update(overrides)
    return AlertCreate(**defaults)


def build_alert_model(**overrides) -> Alert:
    """Build Alert model with sensible defaults."""
    defaults = {
        "id": uuid4(),
        "alert_type": "TRANSACTION_RISK",
        "severity": AlertSeverity.MEDIUM,
        "status": AlertStatus.NEW,
        "client_id": uuid4(),
        "transaction_id": uuid4(),
        "document_id": None,
        "title": "Test alert",
        "description": "Test description",
        "risk_score": 50,
        "triggered_rules": {"rule1": True},
        "context": {"key": "value"},
        "recommended_actions": ["Review manually"],
        "assigned_to": None,
        "resolved_at": None,
        "resolution_notes": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    defaults.update(overrides)
    return Alert(**defaults)


def mock_db_refresh(obj):
    """
    Simulate database refresh populating auto-generated fields.

    Use as side_effect for mock_db.refresh:
        mock_db.refresh = AsyncMock(side_effect=mock_db_refresh)
    """
    if not hasattr(obj, 'id') or obj.id is None:
        obj.id = uuid4()
    if not hasattr(obj, 'created_at') or obj.created_at is None:
        obj.created_at = datetime.utcnow()
    if not hasattr(obj, 'updated_at') or obj.updated_at is None:
        obj.updated_at = datetime.utcnow()


# ============================================================================
# Initialization Tests
# ============================================================================


@pytest.mark.unit
def test_alert_service_initializes():
    """Test AlertService initializes with database session."""
    mock_db = AsyncMock(spec=AsyncSession)

    service = AlertService(db=mock_db)

    assert service.db == mock_db


# ============================================================================
# Create Alert Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_alert_success():
    """Test creating alert successfully."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_data = build_alert_create()

    # Mock database operations - simulate database populating fields
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock(side_effect=mock_db_refresh)

    # Act
    result = await service.create_alert(alert_data)

    # Assert
    assert result.alert_type == alert_data.alert_type
    assert result.severity == alert_data.severity
    assert result.status == AlertStatus.NEW  # Default status
    assert result.id is not None  # Database should populate ID
    assert result.created_at is not None  # Database should populate created_at
    assert result.updated_at is not None  # Database should populate updated_at
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_alert_sets_default_status():
    """Test creating alert sets default status to NEW."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_data = build_alert_create()

    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock(side_effect=mock_db_refresh)

    # Act
    result = await service.create_alert(alert_data)

    # Assert
    assert result.status == AlertStatus.NEW


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_alert_with_high_severity():
    """Test creating high-severity alert."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_data = build_alert_create(
        severity=AlertSeverity.HIGH,
        risk_score=85
    )

    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock(side_effect=mock_db_refresh)

    # Act
    result = await service.create_alert(alert_data)

    # Assert
    assert result.severity == AlertSeverity.HIGH
    assert result.risk_score == 85


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_alert_with_document_id():
    """Test creating alert with document_id."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    document_id = uuid4()
    alert_data = build_alert_create(document_id=document_id)

    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock(side_effect=mock_db_refresh)

    # Act
    result = await service.create_alert(alert_data)

    # Assert
    assert result.document_id == document_id


# ============================================================================
# Get Alert Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_alert_found():
    """Test getting existing alert by ID."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_id = uuid4()
    alert_model = build_alert_model(id=alert_id)

    # Mock database query
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = alert_model
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Act
    result = await service.get_alert(alert_id)

    # Assert
    assert result is not None
    assert result.id == alert_id
    mock_db.execute.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_alert_not_found():
    """Test getting non-existent alert returns None."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_id = uuid4()

    # Mock database query returning None
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Act
    result = await service.get_alert(alert_id)

    # Assert
    assert result is None


# ============================================================================
# List Alerts Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_alerts_no_filters():
    """Test listing all alerts without filters."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alerts = [
        build_alert_model(id=uuid4()),
        build_alert_model(id=uuid4()),
        build_alert_model(id=uuid4()),
    ]

    # Mock database query
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = alerts
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Act
    result = await service.list_alerts()

    # Assert
    assert len(result) == 3
    mock_db.execute.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_alerts_filter_by_client_id():
    """Test listing alerts filtered by client_id."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    client_id = uuid4()
    alerts = [
        build_alert_model(id=uuid4(), client_id=client_id),
        build_alert_model(id=uuid4(), client_id=client_id),
    ]

    # Mock database query
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = alerts
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Act
    result = await service.list_alerts(client_id=client_id)

    # Assert
    assert len(result) == 2
    assert all(a.client_id == client_id for a in result)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_alerts_filter_by_status():
    """Test listing alerts filtered by status."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alerts = [
        build_alert_model(id=uuid4(), status=AlertStatus.NEW),
        build_alert_model(id=uuid4(), status=AlertStatus.NEW),
    ]

    # Mock database query
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = alerts
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Act
    result = await service.list_alerts(status=AlertStatus.NEW)

    # Assert
    assert len(result) == 2
    assert all(a.status == AlertStatus.NEW for a in result)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_alerts_filter_by_severity():
    """Test listing alerts filtered by severity."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alerts = [
        build_alert_model(id=uuid4(), severity=AlertSeverity.HIGH),
        build_alert_model(id=uuid4(), severity=AlertSeverity.HIGH),
    ]

    # Mock database query
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = alerts
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Act
    result = await service.list_alerts(severity=AlertSeverity.HIGH)

    # Assert
    assert len(result) == 2
    assert all(a.severity == AlertSeverity.HIGH for a in result)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_alerts_with_pagination():
    """Test listing alerts with skip and limit."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alerts = [build_alert_model(id=uuid4())]

    # Mock database query
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = alerts
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Act
    result = await service.list_alerts(skip=10, limit=20)

    # Assert
    assert len(result) == 1
    # Verify query was constructed with offset and limit


# ============================================================================
# Update Alert Status Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_alert_status_success():
    """Test updating alert status successfully."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_id = uuid4()
    alert_model = build_alert_model(id=alert_id, status=AlertStatus.ACKNOWLEDGED)

    # Mock database execute to return updated alert
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=alert_model)
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    # Act
    result = await service.update_alert_status(alert_id, AlertStatus.ACKNOWLEDGED)

    # Assert
    assert result.status == AlertStatus.ACKNOWLEDGED
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_alert_status_sets_resolved_at():
    """Test updating status to RESOLVED sets resolved_at timestamp."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_id = uuid4()
    alert_model = build_alert_model(id=alert_id, status=AlertStatus.RESOLVED, resolved_at=datetime.utcnow())

    # Mock database execute to return updated alert
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=alert_model)
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    # Act
    result = await service.update_alert_status(
        alert_id,
        AlertStatus.RESOLVED,
        resolution_notes="Issue fixed"
    )

    # Assert
    assert result.status == AlertStatus.RESOLVED
    assert result.resolved_at is not None  # resolved_at should be set


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_alert_status_not_found():
    """Test updating non-existent alert returns None."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_id = uuid4()

    # Mock database execute to return None (alert not found)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    # Act
    result = await service.update_alert_status(alert_id, AlertStatus.ACKNOWLEDGED)

    # Assert
    assert result is None


# ============================================================================
# Assign Alert Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assign_alert_success():
    """Test assigning alert to user successfully."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_id = uuid4()
    user_id = uuid4()
    alert_model = build_alert_model(id=alert_id, assigned_to=user_id)

    # Mock database execute - first call gets current alert, second call updates it
    mock_result_select = MagicMock()
    mock_result_select.scalar_one_or_none = MagicMock(return_value=alert_model)

    mock_result_update = MagicMock()
    mock_result_update.scalar_one_or_none = MagicMock(return_value=alert_model)

    mock_db.execute = AsyncMock(side_effect=[mock_result_select, mock_result_update])
    mock_db.commit = AsyncMock()

    # Act
    result = await service.assign_alert(alert_id, user_id)

    # Assert
    assert result.assigned_to == user_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assign_alert_updates_status_to_acknowledged():
    """Test assigning alert updates status to ACKNOWLEDGED if NEW."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_id = uuid4()
    user_id = uuid4()
    alert_model_new = build_alert_model(id=alert_id, status=AlertStatus.NEW, assigned_to=None)
    alert_model_updated = build_alert_model(id=alert_id, status=AlertStatus.ACKNOWLEDGED, assigned_to=user_id)

    # Mock database execute - first call gets current alert (NEW), second call updates it (ACKNOWLEDGED)
    mock_result_select = MagicMock()
    mock_result_select.scalar_one_or_none = MagicMock(return_value=alert_model_new)

    mock_result_update = MagicMock()
    mock_result_update.scalar_one_or_none = MagicMock(return_value=alert_model_updated)

    mock_db.execute = AsyncMock(side_effect=[mock_result_select, mock_result_update])
    mock_db.commit = AsyncMock()

    # Act
    result = await service.assign_alert(alert_id, user_id)

    # Assert
    assert result.status == AlertStatus.ACKNOWLEDGED


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assign_alert_not_found():
    """Test assigning non-existent alert returns None."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_id = uuid4()
    user_id = uuid4()

    # Mock database execute - both calls return None (alert not found)
    mock_result_select = MagicMock()
    mock_result_select.scalar_one_or_none = MagicMock(return_value=None)

    mock_result_update = MagicMock()
    mock_result_update.scalar_one_or_none = MagicMock(return_value=None)

    mock_db.execute = AsyncMock(side_effect=[mock_result_select, mock_result_update])
    mock_db.commit = AsyncMock()

    # Act
    result = await service.assign_alert(alert_id, user_id)

    # Assert
    assert result is None


# ============================================================================
# Delete Alert Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_alert_success():
    """Test deleting alert successfully."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_id = uuid4()

    # Mock database delete
    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    # Act
    result = await service.delete_alert(alert_id)

    # Assert
    assert result is True
    mock_db.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_alert_not_found():
    """Test deleting non-existent alert returns False."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_id = uuid4()

    # Mock database delete with 0 rows affected
    mock_result = MagicMock()
    mock_result.rowcount = 0
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    # Act
    result = await service.delete_alert(alert_id)

    # Assert
    assert result is False


# ============================================================================
# Get Critical Alerts Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_critical_alerts():
    """Test getting critical alerts (CRITICAL severity, not resolved)."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alerts = [
        build_alert_model(id=uuid4(), severity=AlertSeverity.CRITICAL, status=AlertStatus.NEW),
        build_alert_model(id=uuid4(), severity=AlertSeverity.CRITICAL, status=AlertStatus.ESCALATED),
    ]

    # Mock database query
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = alerts
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Act
    result = await service.get_critical_alerts()

    # Assert
    assert len(result) == 2
    assert all(a.severity == AlertSeverity.CRITICAL for a in result)


# ============================================================================
# Edge Cases Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_alert_with_null_optional_fields():
    """Test creating alert with null optional fields."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_data = build_alert_create(
        transaction_id=None,
        document_id=None,
        description=None,
    )

    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock(side_effect=mock_db_refresh)

    # Act
    result = await service.create_alert(alert_data)

    # Assert
    assert result.transaction_id is None
    assert result.document_id is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_alerts_empty_result():
    """Test listing alerts returns empty list when no alerts exist."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    # Mock empty result
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Act
    result = await service.list_alerts()

    # Assert
    assert result == []


# ============================================================================
# Parametrized Status Transition Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("initial_status,new_status", [
    (AlertStatus.NEW, AlertStatus.ACKNOWLEDGED),
    (AlertStatus.ACKNOWLEDGED, AlertStatus.IN_REVIEW),
    (AlertStatus.IN_REVIEW, AlertStatus.ESCALATED),
    (AlertStatus.IN_REVIEW, AlertStatus.RESOLVED),
    (AlertStatus.ESCALATED, AlertStatus.RESOLVED),
])
async def test_status_transitions(initial_status, new_status):
    """Test various alert status transitions."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_id = uuid4()
    alert_model = build_alert_model(id=alert_id, status=new_status)

    # Mock database execute to return updated alert
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=alert_model)
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()

    # Act
    result = await service.update_alert_status(alert_id, new_status)

    # Assert
    assert result.status == new_status


# ============================================================================
# Parametrized Severity Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("severity", [
    AlertSeverity.LOW,
    AlertSeverity.MEDIUM,
    AlertSeverity.HIGH,
    AlertSeverity.CRITICAL,
])
async def test_create_alert_with_different_severities(severity):
    """Test creating alerts with different severity levels."""
    # Arrange
    mock_db = AsyncMock(spec=AsyncSession)
    service = AlertService(db=mock_db)

    alert_data = build_alert_create(severity=severity)

    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock(side_effect=mock_db_refresh)

    # Act
    result = await service.create_alert(alert_data)

    # Assert
    assert result.severity == severity
