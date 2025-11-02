from fastapi import APIRouter, HTTPException
from models.schemas import Alert, DashboardSummary, AlertDetails, RemediateResponse
from services.mock_data import (
    get_dashboard_summary,
    get_active_alerts,
    get_alert_details,
)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/summary", response_model=DashboardSummary)
async def get_summary():
    """Get dashboard summary with KPIs"""
    return get_dashboard_summary()


@router.get("/active", response_model=list[Alert])
async def get_alerts():
    """Get list of active alerts"""
    return get_active_alerts()


@router.get("/{alert_id}", response_model=AlertDetails)
async def get_alert(alert_id: str):
    """Get detailed information for a specific alert"""
    try:
        return get_alert_details(alert_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Alert not found")


@router.post("/{alert_id}/remediate", response_model=RemediateResponse)
async def remediate_alert(alert_id: str):
    """Mark an alert as remediated"""
    # In production, this would update the database and create audit log
    return RemediateResponse(
        success=True,
        message=f"Alert {alert_id} has been marked for remediation"
    )

