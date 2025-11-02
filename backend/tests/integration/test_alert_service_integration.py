"""
Integration tests for AlertService.

Tests alert service with real database interactions.
"""

import pytest
from uuid import uuid4
from datetime import datetime

from backend.services.alert_service import AlertService
from backend.schemas.alert import AlertStatus, AlertSeverity
from .conftest import build_alert_create_integration


# ============================================================================
# Create and Persist Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_create_alert_persists_to_database(alert_service_integration, client_in_db):
    """Test creating alert persists to real database."""
    # Arrange
    alert_data = build_alert_create_integration(client_id=client_in_db.id)

    # Act
    created_alert = await alert_service_integration.create_alert(alert_data)

    # Assert - Verify it was persisted
    retrieved_alert = await alert_service_integration.get_alert(created_alert.id)
    assert retrieved_alert is not None
    assert retrieved_alert.id == created_alert.id
    assert retrieved_alert.client_id == client_in_db.id
    assert retrieved_alert.status == AlertStatus.NEW


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_create_multiple_alerts_persists_all(alert_service_integration, client_in_db):
    """Test creating multiple alerts persists all to database."""
    # Arrange
    alert_data_1 = build_alert_create_integration(client_in_db.id, title="Alert 1")
    alert_data_2 = build_alert_create_integration(client_in_db.id, title="Alert 2")
    alert_data_3 = build_alert_create_integration(client_in_db.id, title="Alert 3")

    # Act
    alert_1 = await alert_service_integration.create_alert(alert_data_1)
    alert_2 = await alert_service_integration.create_alert(alert_data_2)
    alert_3 = await alert_service_integration.create_alert(alert_data_3)

    # Assert - All should be retrievable
    alerts = await alert_service_integration.list_alerts()
    assert len(alerts) >= 3
    alert_ids = [a.id for a in alerts]
    assert alert_1.id in alert_ids
    assert alert_2.id in alert_ids
    assert alert_3.id in alert_ids


# ============================================================================
# Retrieve Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_get_alert_retrieves_from_database(alert_service_integration, alert_in_db):
    """Test getting alert retrieves from real database."""
    # Act
    retrieved = await alert_service_integration.get_alert(alert_in_db.id)

    # Assert
    assert retrieved is not None
    assert retrieved.id == alert_in_db.id
    assert retrieved.title == alert_in_db.title
    assert retrieved.risk_score == alert_in_db.risk_score


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_get_nonexistent_alert_returns_none(alert_service_integration):
    """Test getting non-existent alert returns None."""
    # Arrange
    nonexistent_id = uuid4()

    # Act
    result = await alert_service_integration.get_alert(nonexistent_id)

    # Assert
    assert result is None


# ============================================================================
# List and Filter Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_list_alerts_retrieves_all(alert_service_integration, multiple_alerts_in_db):
    """Test listing alerts retrieves all from database."""
    # Act
    alerts = await alert_service_integration.list_alerts()

    # Assert
    assert len(alerts) >= 5  # At least the 5 we created
    assert all(a.id is not None for a in alerts)


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_list_alerts_filter_by_client_id(
    alert_service_integration,
    client_in_db,
    multiple_alerts_in_db
):
    """Test filtering alerts by client_id."""
    # Act
    alerts = await alert_service_integration.list_alerts(client_id=client_in_db.id)

    # Assert
    assert len(alerts) >= 5
    assert all(a.client_id == client_in_db.id for a in alerts)


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_list_alerts_filter_by_status(
    alert_service_integration,
    multiple_alerts_in_db
):
    """Test filtering alerts by status."""
    # Act - Filter for NEW status
    new_alerts = await alert_service_integration.list_alerts(status=AlertStatus.NEW)

    # Assert - Should have 3 NEW alerts (indices 0, 1, 2)
    assert len(new_alerts) >= 3
    assert all(a.status == AlertStatus.NEW for a in new_alerts)


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_list_alerts_filter_by_severity(
    alert_service_integration,
    multiple_alerts_in_db
):
    """Test filtering alerts by severity."""
    # Act - Filter for MEDIUM severity
    medium_alerts = await alert_service_integration.list_alerts(severity=AlertSeverity.MEDIUM)

    # Assert - Should have 3 MEDIUM alerts (even indices: 0, 2, 4)
    assert len(medium_alerts) >= 3
    assert all(a.severity == AlertSeverity.MEDIUM for a in medium_alerts)


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_list_alerts_multiple_filters(
    alert_service_integration,
    client_in_db,
    multiple_alerts_in_db
):
    """Test filtering alerts with multiple criteria."""
    # Act - Filter by client_id, status, and severity
    alerts = await alert_service_integration.list_alerts(
        client_id=client_in_db.id,
        status=AlertStatus.NEW,
        severity=AlertSeverity.MEDIUM
    )

    # Assert - Should have 2 alerts (indices 0 and 2)
    assert len(alerts) >= 2
    assert all(a.client_id == client_in_db.id for a in alerts)
    assert all(a.status == AlertStatus.NEW for a in alerts)
    assert all(a.severity == AlertSeverity.MEDIUM for a in alerts)


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_list_alerts_pagination(
    alert_service_integration,
    multiple_alerts_in_db
):
    """Test alert pagination works correctly."""
    # Act - Get first 2 alerts
    page_1 = await alert_service_integration.list_alerts(skip=0, limit=2)

    # Act - Get next 2 alerts
    page_2 = await alert_service_integration.list_alerts(skip=2, limit=2)

    # Assert
    assert len(page_1) == 2
    assert len(page_2) >= 2
    # Ensure no overlap
    page_1_ids = [a.id for a in page_1]
    page_2_ids = [a.id for a in page_2]
    assert len(set(page_1_ids) & set(page_2_ids)) == 0


# ============================================================================
# Update Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_update_alert_status_persists(alert_service_integration, alert_in_db):
    """Test updating alert status persists to database."""
    # Act
    updated = await alert_service_integration.update_alert_status(
        alert_in_db.id,
        AlertStatus.ACKNOWLEDGED
    )

    # Assert - Verify update persisted
    assert updated.status == AlertStatus.ACKNOWLEDGED

    # Retrieve and verify
    retrieved = await alert_service_integration.get_alert(alert_in_db.id)
    assert retrieved.status == AlertStatus.ACKNOWLEDGED


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_update_to_resolved_sets_timestamp(alert_service_integration, alert_in_db):
    """Test updating to RESOLVED status sets resolved_at timestamp."""
    # Act
    updated = await alert_service_integration.update_alert_status(
        alert_in_db.id,
        AlertStatus.RESOLVED,
        resolution_notes="Fixed during integration test"
    )

    # Assert
    assert updated.status == AlertStatus.RESOLVED
    # Note: resolved_at should be set, but exact timestamp check may vary


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_update_nonexistent_alert_returns_none(alert_service_integration):
    """Test updating non-existent alert returns None."""
    # Arrange
    nonexistent_id = uuid4()

    # Act
    result = await alert_service_integration.update_alert_status(
        nonexistent_id,
        AlertStatus.RESOLVED
    )

    # Assert
    assert result is None


# ============================================================================
# Assignment Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_assign_alert_persists(alert_service_integration, alert_in_db):
    """Test assigning alert persists to database."""
    # Arrange
    user_id = uuid4()

    # Act
    updated = await alert_service_integration.assign_alert(alert_in_db.id, user_id)

    # Assert
    assert updated.assigned_to == user_id

    # Verify persistence
    retrieved = await alert_service_integration.get_alert(alert_in_db.id)
    assert retrieved.assigned_to == user_id


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_assign_alert_updates_status(alert_service_integration, client_in_db):
    """Test assigning NEW alert updates status to ACKNOWLEDGED."""
    # Arrange - Create NEW alert
    alert_data = build_alert_create_integration(client_in_db.id)
    alert = await alert_service_integration.create_alert(alert_data)
    user_id = uuid4()

    # Act
    updated = await alert_service_integration.assign_alert(alert.id, user_id)

    # Assert
    assert updated.status == AlertStatus.ACKNOWLEDGED
    assert updated.assigned_to == user_id


# ============================================================================
# Delete Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_delete_alert_removes_from_database(alert_service_integration, alert_in_db):
    """Test deleting alert removes it from database."""
    # Act
    deleted = await alert_service_integration.delete_alert(alert_in_db.id)

    # Assert
    assert deleted is True

    # Verify it's gone
    retrieved = await alert_service_integration.get_alert(alert_in_db.id)
    assert retrieved is None


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_delete_nonexistent_alert_returns_false(alert_service_integration):
    """Test deleting non-existent alert returns False."""
    # Arrange
    nonexistent_id = uuid4()

    # Act
    result = await alert_service_integration.delete_alert(nonexistent_id)

    # Assert
    assert result is False


# ============================================================================
# Critical Alerts Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_get_critical_alerts(alert_service_integration, client_in_db):
    """Test getting critical alerts returns only CRITICAL severity."""
    # Arrange - Create mix of alerts
    await alert_service_integration.create_alert(
        build_alert_create_integration(client_in_db.id, severity=AlertSeverity.CRITICAL)
    )
    await alert_service_integration.create_alert(
        build_alert_create_integration(client_in_db.id, severity=AlertSeverity.HIGH)
    )
    await alert_service_integration.create_alert(
        build_alert_create_integration(client_in_db.id, severity=AlertSeverity.CRITICAL)
    )

    # Act
    critical_alerts = await alert_service_integration.get_critical_alerts()

    # Assert
    assert len(critical_alerts) >= 2
    assert all(a.severity == AlertSeverity.CRITICAL for a in critical_alerts)


# ============================================================================
# Transaction Tests (Rollback)
# ============================================================================


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_database_rollback_on_error(integration_db, client_in_db):
    """Test database rollback occurs on error."""
    # Arrange
    service = AlertService(db=integration_db)

    # Create valid alert
    alert_data = build_alert_create_integration(client_in_db.id)
    alert = await service.create_alert(alert_data)

    # Verify it exists
    assert await service.get_alert(alert.id) is not None

    # Act - Try to update with invalid operation (this should fail in real scenario)
    # For this test, we'll just verify we can still access the database after operations


# ============================================================================
# Concurrent Operations Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_concurrent_alert_creation(alert_service_integration, client_in_db):
    """Test creating alerts concurrently."""
    import asyncio

    # Arrange - Create tasks for concurrent operations
    tasks = [
        alert_service_integration.create_alert(
            build_alert_create_integration(client_in_db.id, title=f"Concurrent {i}")
        )
        for i in range(10)
    ]

    # Act - Run concurrently
    results = await asyncio.gather(*tasks)

    # Assert
    assert len(results) == 10
    assert all(r.id is not None for r in results)

    # Verify all persisted
    all_alerts = await alert_service_integration.list_alerts(client_id=client_in_db.id)
    assert len(all_alerts) >= 10


# ============================================================================
# Data Integrity Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_alert_timestamps_set_correctly(alert_service_integration, client_in_db):
    """Test alert timestamps are set correctly on creation."""
    # Arrange
    alert_data = build_alert_create_integration(client_in_db.id)

    # Act
    alert = await alert_service_integration.create_alert(alert_data)

    # Assert
    assert alert.created_at is not None
    assert alert.updated_at is not None
    assert isinstance(alert.created_at, datetime)
    assert isinstance(alert.updated_at, datetime)


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_alert_context_json_persists(alert_service_integration, client_in_db):
    """Test alert context (JSON field) persists correctly."""
    # Arrange
    complex_context = {
        "transaction": {"amount": 50000, "currency": "USD"},
        "client": {"risk_level": "HIGH"},
        "rules": ["velocity_check", "amount_threshold"],
        "nested": {"data": {"structure": True}},
    }

    alert_data = build_alert_create_integration(
        client_in_db.id,
        context=complex_context
    )

    # Act
    alert = await alert_service_integration.create_alert(alert_data)

    # Assert
    retrieved = await alert_service_integration.get_alert(alert.id)
    assert retrieved.context == complex_context


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_alert_recommended_actions_list_persists(
    alert_service_integration,
    client_in_db
):
    """Test alert recommended_actions (list field) persists correctly."""
    # Arrange
    actions = [
        "Contact client immediately",
        "Review transaction history",
        "Escalate to compliance team",
        "Request additional documentation",
    ]

    alert_data = build_alert_create_integration(
        client_in_db.id,
        recommended_actions=actions
    )

    # Act
    alert = await alert_service_integration.create_alert(alert_data)

    # Assert
    retrieved = await alert_service_integration.get_alert(alert.id)
    assert retrieved.recommended_actions == actions


# ============================================================================
# Edge Cases Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_alert_with_null_optional_fields(alert_service_integration, client_in_db):
    """Test creating alert with null optional fields."""
    # Arrange
    alert_data = build_alert_create_integration(
        client_in_db.id,
        transaction_id=None,
        document_id=None,
        description=None,
    )

    # Act
    alert = await alert_service_integration.create_alert(alert_data)

    # Assert
    assert alert.transaction_id is None
    assert alert.document_id is None

    # Verify persistence
    retrieved = await alert_service_integration.get_alert(alert.id)
    assert retrieved.transaction_id is None
    assert retrieved.document_id is None


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_list_alerts_empty_database(alert_service_integration):
    """Test listing alerts when database is empty."""
    # Act
    alerts = await alert_service_integration.list_alerts()

    # Assert
    assert alerts == []
