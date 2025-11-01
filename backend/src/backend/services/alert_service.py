"""
Alert management service.

Single Responsibility: Manage alerts (CRUD operations, status updates, assignment).
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Alert, AlertRecipient
from backend.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertStatus,
    AlertSeverity,
)
from backend.logging import get_logger

logger = get_logger(__name__)


class AlertService:
    """
    Service for managing compliance alerts.

    Responsibilities:
    - Create alerts from risk analysis
    - Update alert status and assignments
    - Query alerts with filtering
    - Manage alert lifecycle
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize alert service.

        Args:
            db: Database session (injected via FastAPI Depends)
        """
        self.db = db
        logger.debug("alert_service_initialized")

    async def create_alert(self, alert_data: AlertCreate) -> AlertResponse:
        """
        Create a new alert.

        Args:
            alert_data: Alert creation data

        Returns:
            Created alert
        """
        logger.info(
            "creating_alert",
            alert_type=alert_data.alert_type,
            severity=alert_data.severity,
            client_id=str(alert_data.client_id),
        )

        # Create alert entity
        alert = Alert(
            alert_type=alert_data.alert_type,
            severity=alert_data.severity,
            status=AlertStatus.NEW,
            client_id=alert_data.client_id,
            transaction_id=alert_data.transaction_id,
            document_id=alert_data.document_id,
            title=alert_data.title,
            description=alert_data.description,
            risk_score=alert_data.risk_score,
            triggered_rules=alert_data.triggered_rules,
            context=alert_data.context,
            recommended_actions=alert_data.recommended_actions,
        )

        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)

        logger.info("alert_created", alert_id=str(alert.id), risk_score=alert.risk_score)

        return AlertResponse.model_validate(alert)

    async def get_alert(self, alert_id: UUID) -> Optional[AlertResponse]:
        """
        Get alert by ID.

        Args:
            alert_id: Alert UUID

        Returns:
            Alert if found, None otherwise
        """
        logger.debug("fetching_alert", alert_id=str(alert_id))

        result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()

        if alert:
            return AlertResponse.model_validate(alert)

        logger.warning("alert_not_found", alert_id=str(alert_id))
        return None

    async def list_alerts(
        self,
        client_id: Optional[UUID] = None,
        status: Optional[AlertStatus] = None,
        severity: Optional[AlertSeverity] = None,
        alert_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AlertResponse]:
        """
        List alerts with optional filtering.

        Args:
            client_id: Filter by client
            status: Filter by status
            severity: Filter by severity
            alert_type: Filter by alert type
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            List of alerts
        """
        logger.debug(
            "listing_alerts",
            client_id=str(client_id) if client_id else None,
            status=status,
            severity=severity,
            alert_type=alert_type,
            skip=skip,
            limit=limit,
        )

        # Build query with filters
        query = select(Alert)

        filters = []
        if client_id:
            filters.append(Alert.client_id == client_id)
        if status:
            filters.append(Alert.status == status)
        if severity:
            filters.append(Alert.severity == severity)
        if alert_type:
            filters.append(Alert.alert_type == alert_type)

        if filters:
            query = query.where(and_(*filters))

        # Order by created date (newest first)
        query = query.order_by(Alert.created_at.desc())

        # Pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        alerts = result.scalars().all()

        logger.info("alerts_listed", count=len(alerts))

        return [AlertResponse.model_validate(alert) for alert in alerts]

    async def update_alert_status(
        self,
        alert_id: UUID,
        status: AlertStatus,
        resolution_notes: Optional[str] = None,
    ) -> Optional[AlertResponse]:
        """
        Update alert status.

        Args:
            alert_id: Alert UUID
            status: New status
            resolution_notes: Optional resolution notes

        Returns:
            Updated alert if found, None otherwise
        """
        logger.info(
            "updating_alert_status",
            alert_id=str(alert_id),
            status=status,
        )

        # Prepare update data
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow(),
        }

        if resolution_notes:
            update_data["resolution_notes"] = resolution_notes

        # If status is RESOLVED, set resolved timestamp
        if status == AlertStatus.RESOLVED:
            update_data["resolved_at"] = datetime.utcnow()

        # Execute update
        result = await self.db.execute(
            update(Alert).where(Alert.id == alert_id).values(**update_data).returning(Alert)
        )

        await self.db.commit()

        alert = result.scalar_one_or_none()

        if alert:
            logger.info("alert_status_updated", alert_id=str(alert_id), new_status=status)
            return AlertResponse.model_validate(alert)

        logger.warning("alert_not_found_for_update", alert_id=str(alert_id))
        return None

    async def update_alert(self, alert_id: UUID, alert_data: AlertUpdate) -> Optional[AlertResponse]:
        """
        Update alert details.

        Args:
            alert_id: Alert UUID
            alert_data: Alert update data

        Returns:
            Updated alert if found, None otherwise
        """
        logger.info("updating_alert", alert_id=str(alert_id))

        # Build update dictionary (only include provided fields)
        update_dict = alert_data.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()

        result = await self.db.execute(
            update(Alert).where(Alert.id == alert_id).values(**update_dict).returning(Alert)
        )

        await self.db.commit()

        alert = result.scalar_one_or_none()

        if alert:
            logger.info("alert_updated", alert_id=str(alert_id))
            return AlertResponse.model_validate(alert)

        logger.warning("alert_not_found_for_update", alert_id=str(alert_id))
        return None

    async def delete_alert(self, alert_id: UUID) -> bool:
        """
        Delete alert.

        Args:
            alert_id: Alert UUID

        Returns:
            True if deleted, False if not found
        """
        logger.warning("deleting_alert", alert_id=str(alert_id))

        result = await self.db.execute(delete(Alert).where(Alert.id == alert_id))
        await self.db.commit()

        deleted = result.rowcount > 0

        if deleted:
            logger.info("alert_deleted", alert_id=str(alert_id))
        else:
            logger.warning("alert_not_found_for_deletion", alert_id=str(alert_id))

        return deleted

    async def assign_alert(
        self,
        alert_id: UUID,
        assigned_to_user_id: UUID,
        assigned_to_role: Optional[str] = None,
    ) -> Optional[AlertResponse]:
        """
        Assign alert to user/role.

        Args:
            alert_id: Alert UUID
            assigned_to_user_id: User UUID to assign to
            assigned_to_role: Optional role designation

        Returns:
            Updated alert if found, None otherwise
        """
        logger.info(
            "assigning_alert",
            alert_id=str(alert_id),
            assigned_to=str(assigned_to_user_id),
            role=assigned_to_role,
        )

        update_data = {
            "assigned_to": assigned_to_user_id,
            "assigned_role": assigned_to_role,
            "assigned_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        # If not already acknowledged, mark as such
        result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()

        if alert and alert.status == AlertStatus.NEW:
            update_data["status"] = AlertStatus.ACKNOWLEDGED

        result = await self.db.execute(
            update(Alert).where(Alert.id == alert_id).values(**update_data).returning(Alert)
        )

        await self.db.commit()

        alert = result.scalar_one_or_none()

        if alert:
            logger.info("alert_assigned", alert_id=str(alert_id))
            return AlertResponse.model_validate(alert)

        logger.warning("alert_not_found_for_assignment", alert_id=str(alert_id))
        return None

    async def get_critical_alerts(self, client_id: Optional[UUID] = None) -> List[AlertResponse]:
        """
        Get all critical severity alerts that are not resolved.

        Args:
            client_id: Optional client filter

        Returns:
            List of critical alerts
        """
        logger.info("fetching_critical_alerts", client_id=str(client_id) if client_id else None)

        query = select(Alert).where(
            and_(
                Alert.severity == AlertSeverity.CRITICAL,
                Alert.status.in_([AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.IN_REVIEW]),
            )
        )

        if client_id:
            query = query.where(Alert.client_id == client_id)

        query = query.order_by(Alert.created_at.desc())

        result = await self.db.execute(query)
        alerts = result.scalars().all()

        logger.info("critical_alerts_fetched", count=len(alerts))

        return [AlertResponse.model_validate(alert) for alert in alerts]


__all__ = ["AlertService"]
