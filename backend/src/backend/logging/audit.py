"""
Audit logging for compliance-critical events.

Provides specialized logging for KYC, document validation, and risk decisions.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

import structlog

from backend.database.models import AuditLog
from backend.database import get_db

logger = structlog.get_logger(__name__)


class AuditLogger:
    """
    Specialized logger for audit trail.

    Logs all compliance-critical events with full context and stores
    them in the database for immutable audit trail.
    """

    @staticmethod
    async def log(
        event_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        user_role: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        action: Optional[str] = None,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
        severity: str = "AUDIT",
        **kwargs,
    ) -> None:
        """
        Log audit event to both structlog and database.

        Args:
            event_type: Type of event (e.g., "document_uploaded", "kyc_updated")
            entity_type: Type of entity (DOCUMENT, CLIENT, TRANSACTION, ALERT)
            entity_id: ID of entity
            user_id: User who performed action
            user_role: Role of user (RM, COMPLIANCE, LEGAL)
            session_id: Session ID for correlation
            ip_address: IP address of request
            action: Action performed (CREATE, UPDATE, DELETE, APPROVE, REJECT)
            before_state: State before action
            after_state: State after action
            severity: Log severity (INFO, WARNING, ERROR, AUDIT)
            **kwargs: Additional context

        Example:
            await audit_logger.log(
                event_type="document_uploaded",
                entity_type="DOCUMENT",
                entity_id=doc_id,
                user_id=user.id,
                user_role="RM",
                action="UPLOAD",
                after_state={"filename": "passport.pdf"},
                ip_address="192.168.1.1",
            )
        """
        # Log to structlog (goes to stdout/file)
        logger.log(
            35,  # AUDIT level
            event_type,
            severity=severity,
            timestamp=datetime.utcnow().isoformat(),
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else None,
            user_id=str(user_id) if user_id else None,
            user_role=user_role,
            session_id=session_id,
            ip_address=ip_address,
            action=action,
            before_state=before_state,
            after_state=after_state,
            **kwargs,
        )

        # Store in database for immutable audit trail
        try:
            async for db in get_db():
                audit_entry = AuditLog(
                    timestamp=datetime.utcnow(),
                    event_type=event_type,
                    severity=severity,
                    user_id=user_id,
                    user_role=user_role,
                    session_id=session_id,
                    ip_address=ip_address,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    action=action,
                    before_state=before_state,
                    after_state=after_state,
                    metadata=kwargs if kwargs else None,
                )
                db.add(audit_entry)
                await db.commit()
                break  # Exit after first iteration
        except Exception as e:
            # Don't fail the operation if audit log fails
            logger.error(
                "audit_log_failed",
                error=str(e),
                event_type=event_type,
            )

    @staticmethod
    async def log_document_event(
        event_type: str,
        document_id: UUID,
        user_id: Optional[UUID] = None,
        action: str = None,
        details: Optional[dict] = None,
        **kwargs,
    ) -> None:
        """
        Log document-related event.

        Args:
            event_type: Event type (document_uploaded, document_validated, etc.)
            document_id: Document ID
            user_id: User who performed action
            action: Action performed
            details: Event details
            **kwargs: Additional context
        """
        await AuditLogger.log(
            event_type=event_type,
            entity_type="DOCUMENT",
            entity_id=document_id,
            user_id=user_id,
            action=action,
            after_state=details,
            **kwargs,
        )

    @staticmethod
    async def log_client_event(
        event_type: str,
        client_id: UUID,
        user_id: Optional[UUID] = None,
        action: str = None,
        before_state: Optional[dict] = None,
        after_state: Optional[dict] = None,
        **kwargs,
    ) -> None:
        """
        Log client-related event (KYC updates, risk rating changes).

        Args:
            event_type: Event type (kyc_updated, risk_rating_changed, etc.)
            client_id: Client ID
            user_id: User who performed action
            action: Action performed
            before_state: State before change
            after_state: State after change
            **kwargs: Additional context
        """
        await AuditLogger.log(
            event_type=event_type,
            entity_type="CLIENT",
            entity_id=client_id,
            user_id=user_id,
            action=action,
            before_state=before_state,
            after_state=after_state,
            **kwargs,
        )

    @staticmethod
    async def log_alert_event(
        event_type: str,
        alert_id: UUID,
        user_id: Optional[UUID] = None,
        action: str = None,
        resolution: Optional[dict] = None,
        **kwargs,
    ) -> None:
        """
        Log alert-related event (alert created, acknowledged, resolved).

        Args:
            event_type: Event type (alert_created, alert_resolved, etc.)
            alert_id: Alert ID
            user_id: User who performed action
            action: Action performed
            resolution: Resolution details
            **kwargs: Additional context
        """
        await AuditLogger.log(
            event_type=event_type,
            entity_type="ALERT",
            entity_id=alert_id,
            user_id=user_id,
            action=action,
            after_state=resolution,
            **kwargs,
        )

    @staticmethod
    async def log_risk_decision(
        document_id: UUID,
        risk_score: float,
        risk_level: str,
        user_id: Optional[UUID] = None,
        decision: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Log risk scoring decision (compliance-critical).

        Args:
            document_id: Document ID
            risk_score: Calculated risk score
            risk_level: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
            user_id: User who reviewed
            decision: Decision made (APPROVE, REJECT, ESCALATE)
            **kwargs: Additional context
        """
        await AuditLogger.log(
            event_type="risk_decision",
            entity_type="DOCUMENT",
            entity_id=document_id,
            user_id=user_id,
            action=decision,
            after_state={
                "risk_score": risk_score,
                "risk_level": risk_level,
                "decision": decision,
            },
            severity="AUDIT",
            **kwargs,
        )


# Global instance
audit_logger = AuditLogger()

__all__ = ["AuditLogger", "audit_logger"]
