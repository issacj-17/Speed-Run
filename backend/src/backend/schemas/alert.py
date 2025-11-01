"""Alert management schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field


class AlertStatus(str, Enum):
    """Alert lifecycle status."""

    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_REVIEW = "IN_REVIEW"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(str, Enum):
    """Common alert types."""

    TRANSACTION_RISK = "TRANSACTION_RISK"
    DOCUMENT_RISK = "DOCUMENT_RISK"
    PATTERN_DETECTED = "PATTERN_DETECTED"
    SANCTIONS_MATCH = "SANCTIONS_MATCH"
    PEP_MATCH = "PEP_MATCH"
    FRAUD_INDICATOR = "FRAUD_INDICATOR"
    COMPLIANCE_VIOLATION = "COMPLIANCE_VIOLATION"
    UNUSUAL_ACTIVITY = "UNUSUAL_ACTIVITY"


class AlertCreate(BaseModel):
    """Schema for creating an alert."""

    alert_type: str = Field(description="Type of alert (e.g., TRANSACTION_RISK)")
    severity: AlertSeverity = Field(description="Alert severity level")
    client_id: UUID = Field(description="Client this alert is for")
    transaction_id: Optional[UUID] = Field(None, description="Related transaction ID")
    document_id: Optional[UUID] = Field(None, description="Related document ID")
    title: str = Field(description="Alert title (concise)", max_length=255)
    description: Optional[str] = Field(None, description="Detailed alert description")
    risk_score: int = Field(ge=0, le=100, description="Risk score 0-100")
    triggered_rules: Optional[Dict[str, Any]] = Field(None, description="Rules that triggered alert")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    recommended_actions: Optional[List[str]] = Field(None, description="Suggested actions")

    model_config = {"from_attributes": True}


class AlertUpdate(BaseModel):
    """Schema for updating an alert."""

    alert_type: Optional[str] = None
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    risk_score: Optional[int] = Field(None, ge=0, le=100)
    triggered_rules: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    recommended_actions: Optional[List[str]] = None
    resolution_notes: Optional[str] = None

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    """Schema for alert responses."""

    id: UUID
    alert_type: str
    severity: AlertSeverity
    status: AlertStatus
    client_id: UUID
    transaction_id: Optional[UUID] = None
    document_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    risk_score: int
    triggered_rules: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    recommended_actions: Optional[List[str]] = None
    assigned_to: Optional[UUID] = None
    assigned_role: Optional[str] = None
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertStatusUpdate(BaseModel):
    """Schema for updating alert status."""

    status: AlertStatus = Field(description="New status")
    resolution_notes: Optional[str] = Field(None, description="Notes about resolution")


class AlertAssignment(BaseModel):
    """Schema for assigning an alert."""

    assigned_to_user_id: UUID = Field(description="User ID to assign to")
    assigned_to_role: Optional[str] = Field(None, description="Role designation")


class AlertListResponse(BaseModel):
    """Schema for paginated alert list."""

    alerts: List[AlertResponse]
    total: int
    skip: int
    limit: int


__all__ = [
    "AlertStatus",
    "AlertSeverity",
    "AlertType",
    "AlertCreate",
    "AlertUpdate",
    "AlertResponse",
    "AlertStatusUpdate",
    "AlertAssignment",
    "AlertListResponse",
]
