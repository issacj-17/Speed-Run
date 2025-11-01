"""
Alert management API endpoints.

Provides RESTful API for managing compliance alerts with proper
dependency injection, error handling, and documentation.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from backend.dependencies import (
    get_alert_service,
    pagination_params,
    get_current_active_user,
    require_role,
)
from backend.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertStatusUpdate,
    AlertAssignment,
    AlertStatus,
    AlertSeverity,
)
from backend.services.alert_service import AlertService
from logging import get_logger

logger = get_logger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["alerts"],
    responses={
        404: {"description": "Alert not found"},
        403: {"description": "Insufficient permissions"},
    },
)


@router.post(
    "/",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Alert",
    description="Create a new compliance alert from risk analysis",
)
async def create_alert(
    alert_data: AlertCreate,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: dict = Depends(get_current_active_user),
) -> AlertResponse:
    """
    Create a new alert.

    Args:
        alert_data: Alert creation data
        alert_service: Alert service (injected)
        current_user: Current user (injected)

    Returns:
        Created alert

    Raises:
        HTTPException: If creation fails
    """
    try:
        logger.info(
            "api_create_alert",
            alert_type=alert_data.alert_type,
            severity=alert_data.severity,
            user_id=current_user.get("user_id"),
        )

        alert = await alert_service.create_alert(alert_data)
        return alert

    except Exception as e:
        logger.error("api_create_alert_failed", error=str(e), alert_type=alert_data.alert_type)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert: {str(e)}",
        )


@router.get(
    "/",
    response_model=List[AlertResponse],
    summary="List Alerts",
    description="List alerts with optional filtering and pagination",
)
async def list_alerts(
    client_id: Optional[UUID] = Query(None, description="Filter by client ID"),
    status_filter: Optional[AlertStatus] = Query(None, alias="status", description="Filter by status"),
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    pagination: dict = Depends(pagination_params),
    alert_service: AlertService = Depends(get_alert_service),
    current_user: dict = Depends(get_current_active_user),
) -> List[AlertResponse]:
    """
    List alerts with optional filtering.

    Args:
        client_id: Optional client filter
        status_filter: Optional status filter
        severity: Optional severity filter
        alert_type: Optional type filter
        pagination: Pagination parameters (injected)
        alert_service: Alert service (injected)
        current_user: Current user (injected)

    Returns:
        List of alerts

    Raises:
        HTTPException: If listing fails
    """
    try:
        logger.info(
            "api_list_alerts",
            client_id=str(client_id) if client_id else None,
            status=status_filter,
            user_id=current_user.get("user_id"),
        )

        alerts = await alert_service.list_alerts(
            client_id=client_id,
            status=status_filter,
            severity=severity,
            alert_type=alert_type,
            skip=pagination["skip"],
            limit=pagination["limit"],
        )

        return alerts

    except Exception as e:
        logger.error("api_list_alerts_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list alerts: {str(e)}",
        )


@router.get(
    "/critical",
    response_model=List[AlertResponse],
    summary="Get Critical Alerts",
    description="Get all critical severity alerts that are not resolved",
)
async def get_critical_alerts(
    client_id: Optional[UUID] = Query(None, description="Filter by client ID"),
    alert_service: AlertService = Depends(get_alert_service),
    current_user: dict = Depends(get_current_active_user),
) -> List[AlertResponse]:
    """
    Get critical alerts requiring immediate attention.

    Args:
        client_id: Optional client filter
        alert_service: Alert service (injected)
        current_user: Current user (injected)

    Returns:
        List of critical alerts

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        logger.info(
            "api_get_critical_alerts",
            client_id=str(client_id) if client_id else None,
            user_id=current_user.get("user_id"),
        )

        alerts = await alert_service.get_critical_alerts(client_id=client_id)
        return alerts

    except Exception as e:
        logger.error("api_get_critical_alerts_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get critical alerts: {str(e)}",
        )


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Get Alert",
    description="Get a specific alert by ID",
)
async def get_alert(
    alert_id: UUID,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: dict = Depends(get_current_active_user),
) -> AlertResponse:
    """
    Get alert by ID.

    Args:
        alert_id: Alert UUID
        alert_service: Alert service (injected)
        current_user: Current user (injected)

    Returns:
        Alert

    Raises:
        HTTPException: If alert not found
    """
    logger.info("api_get_alert", alert_id=str(alert_id), user_id=current_user.get("user_id"))

    alert = await alert_service.get_alert(alert_id)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    return alert


@router.put(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Update Alert",
    description="Update alert details",
)
async def update_alert(
    alert_id: UUID,
    alert_data: AlertUpdate,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: dict = Depends(get_current_active_user),
) -> AlertResponse:
    """
    Update alert details.

    Args:
        alert_id: Alert UUID
        alert_data: Update data
        alert_service: Alert service (injected)
        current_user: Current user (injected)

    Returns:
        Updated alert

    Raises:
        HTTPException: If alert not found or update fails
    """
    logger.info("api_update_alert", alert_id=str(alert_id), user_id=current_user.get("user_id"))

    alert = await alert_service.update_alert(alert_id, alert_data)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    return alert


@router.patch(
    "/{alert_id}/status",
    response_model=AlertResponse,
    summary="Update Alert Status",
    description="Update alert status (acknowledge, review, resolve, etc.)",
)
async def update_alert_status(
    alert_id: UUID,
    status_update: AlertStatusUpdate,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: dict = Depends(get_current_active_user),
) -> AlertResponse:
    """
    Update alert status.

    Args:
        alert_id: Alert UUID
        status_update: Status update data
        alert_service: Alert service (injected)
        current_user: Current user (injected)

    Returns:
        Updated alert

    Raises:
        HTTPException: If alert not found or update fails
    """
    logger.info(
        "api_update_alert_status",
        alert_id=str(alert_id),
        new_status=status_update.status,
        user_id=current_user.get("user_id"),
    )

    alert = await alert_service.update_alert_status(
        alert_id=alert_id,
        status=status_update.status,
        resolution_notes=status_update.resolution_notes,
    )

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    return alert


@router.post(
    "/{alert_id}/assign",
    response_model=AlertResponse,
    summary="Assign Alert",
    description="Assign alert to a user or role",
)
async def assign_alert(
    alert_id: UUID,
    assignment: AlertAssignment,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: dict = Depends(get_current_active_user),
) -> AlertResponse:
    """
    Assign alert to user/role.

    Args:
        alert_id: Alert UUID
        assignment: Assignment data
        alert_service: Alert service (injected)
        current_user: Current user (injected)

    Returns:
        Updated alert

    Raises:
        HTTPException: If alert not found or assignment fails
    """
    logger.info(
        "api_assign_alert",
        alert_id=str(alert_id),
        assigned_to=str(assignment.assigned_to_user_id),
        user_id=current_user.get("user_id"),
    )

    alert = await alert_service.assign_alert(
        alert_id=alert_id,
        assigned_to_user_id=assignment.assigned_to_user_id,
        assigned_to_role=assignment.assigned_to_role,
    )

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    return alert


@router.delete(
    "/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Alert",
    description="Delete an alert (admin only)",
)
async def delete_alert(
    alert_id: UUID,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: dict = Depends(require_role("admin")),
) -> None:
    """
    Delete alert (admin only).

    Args:
        alert_id: Alert UUID
        alert_service: Alert service (injected)
        current_user: Current user with admin role (injected)

    Raises:
        HTTPException: If alert not found or deletion fails
    """
    logger.warning(
        "api_delete_alert",
        alert_id=str(alert_id),
        user_id=current_user.get("user_id"),
    )

    deleted = await alert_service.delete_alert(alert_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    return None


# Health check endpoint
@router.get(
    "/health",
    include_in_schema=False,
    summary="Alert Service Health Check",
)
async def health_check() -> dict:
    """
    Health check for alert service.

    Returns:
        dict: Service health status
    """
    return {
        "service": "alerts",
        "status": "healthy",
        "version": "1.0.0",
    }


__all__ = ["router"]
