from datetime import datetime
from models.schemas import (
    Alert, DashboardSummary, TransactionVolume, 
    AgentFinding, DocumentIssue, TransactionHistory, AlertDetails
)

# Mock Alerts
MOCK_ALERTS = [
    Alert(
        alert_id="ALT-789",
        priority="CRITICAL",
        client="ABC Trading Ltd",
        client_id="CLI-456",
        type="Integrated Alert: Transaction + Document Anomaly",
        amount=150000,
        currency="CHF",
        risk_score=95,
        status="pending",
        timestamp=datetime.fromisoformat("2025-10-30T09:15:00"),
    ),
    Alert(
        alert_id="ALT-788",
        priority="HIGH",
        client="Swiss Property Holdings",
        client_id="CLI-203",
        type="Transaction Pattern Anomaly",
        amount=280000,
        currency="CHF",
        risk_score=87,
        status="investigating",
        timestamp=datetime.fromisoformat("2025-10-30T08:45:00"),
    ),
    Alert(
        alert_id="ALT-787",
        priority="HIGH",
        client="Global Investments SA",
        client_id="CLI-891",
        type="Cross-Border Risk",
        amount=95000,
        currency="EUR",
        risk_score=82,
        status="pending",
        timestamp=datetime.fromisoformat("2025-10-30T07:30:00"),
    ),
    Alert(
        alert_id="ALT-786",
        priority="MEDIUM",
        client="Tech Ventures GmbH",
        client_id="CLI-567",
        type="Document Verification Required",
        amount=45000,
        currency="CHF",
        risk_score=68,
        status="pending",
        timestamp=datetime.fromisoformat("2025-10-30T04:20:00"),
    ),
    Alert(
        alert_id="ALT-785",
        priority="MEDIUM",
        client="Alpine Real Estate",
        client_id="CLI-123",
        type="Transaction Volume Spike",
        amount=75000,
        currency="CHF",
        risk_score=55,
        status="resolved",
        timestamp=datetime.fromisoformat("2025-10-30T02:10:00"),
    ),
]

# Mock Dashboard Summary
MOCK_DASHBOARD_SUMMARY = DashboardSummary(
    total_active_alerts=127,
    critical_alerts=8,
    pending_cases=45,
    avg_resolution_time=4.2,
    resolution_time_change=-12,
    alerts_by_risk={
        "critical": 8,
        "high": 23,
        "medium": 51,
        "low": 45,
    },
)

# Mock Transaction Volume
MOCK_TRANSACTION_VOLUME = [
    TransactionVolume(month="Apr", volume=1200),
    TransactionVolume(month="May", volume=1450),
    TransactionVolume(month="Jun", volume=1550),
    TransactionVolume(month="Jul", volume=1480),
    TransactionVolume(month="Aug", volume=1720),
    TransactionVolume(month="Sep", volume=1650),
    TransactionVolume(month="Oct", volume=1850),
]

# Mock Agent Findings
MOCK_AGENT_FINDINGS = [
    AgentFinding(
        agent_name="Agent 1: Regulatory Watcher",
        agent_type="Regulatory Watcher",
        priority="critical",
        finding="Transaction violates FINMA Circular 2025-04 regarding real estate transaction documentation requirements",
        regulation="Regulation: FINMA Circular 2025-04",
    ),
    AgentFinding(
        agent_name="Agent 2: Transaction Analyst",
        agent_type="Transaction Analyst",
        priority="high",
        finding="Amount is 250% above client's 6-month transaction average (CHF 60,000)",
    ),
    AgentFinding(
        agent_name="Agent 3: Document Forensics",
        agent_type="Document Forensics",
        priority="critical",
        finding="Purchase agreement shows signs of digital tampering on page 8",
    ),
]

# Mock Document Issues
MOCK_DOCUMENT_ISSUES = [
    DocumentIssue(
        type="tampering",
        description="Purchase price field shows metadata inconsistency - likely edited after signing",
        page=8,
    ),
    DocumentIssue(
        type="inconsistency",
        description="Signature date conflicts with notary stamp date",
        page=6,
    ),
    DocumentIssue(
        type="suspicious",
        description="Font mismatch detected in beneficiary name field",
        page=3,
    ),
]

# Mock Transaction History
MOCK_TRANSACTION_HISTORY = [
    TransactionHistory(month="2025-04", amount=45000),
    TransactionHistory(month="2025-05", amount=52000),
    TransactionHistory(month="2025-06", amount=61000),
    TransactionHistory(month="2025-07", amount=58000),
    TransactionHistory(month="2025-08", amount=68000),
    TransactionHistory(month="2025-09", amount=55000),
    TransactionHistory(month="2025-10", amount=150000),
]

# Mock Alert Details
MOCK_ALERT_DETAILS = {
    "ALT-788": AlertDetails(
        alert_id="ALT-788",
        priority="HIGH",
        client="ABC Trading Ltd",
        client_id="CLI-456",
        type="Integrated Alert: Transaction + Document Anomaly",
        amount=150000,
        currency="CHF",
        risk_score=95,
        status="pending",
        timestamp=datetime.fromisoformat("2025-10-30T09:15:00"),
        date="30/10/2025",
        country="Switzerland",
        transaction_type="Real Estate Purchase",
        counterparty="Luxury Properties Zurich AG",
        purpose="Purchase of residential property - Zurich",
        agent_findings=MOCK_AGENT_FINDINGS,
        document_issues=MOCK_DOCUMENT_ISSUES,
        transaction_history=MOCK_TRANSACTION_HISTORY,
        document_url="/sample-document.pdf",
    ),
    "ALT-789": AlertDetails(
        alert_id="ALT-789",
        priority="CRITICAL",
        client="ABC Trading Ltd",
        client_id="CLI-456",
        type="Integrated Alert: Transaction + Document Anomaly",
        amount=150000,
        currency="CHF",
        risk_score=95,
        status="pending",
        timestamp=datetime.fromisoformat("2025-10-30T09:15:00"),
        date="30/10/2025",
        country="Switzerland",
        transaction_type="Real Estate Purchase",
        counterparty="Luxury Properties Zurich AG",
        purpose="Purchase of residential property - Zurich",
        agent_findings=MOCK_AGENT_FINDINGS,
        document_issues=MOCK_DOCUMENT_ISSUES,
        transaction_history=MOCK_TRANSACTION_HISTORY,
        document_url="/sample-document.pdf",
    ),
}


def get_dashboard_summary() -> DashboardSummary:
    """Get dashboard summary data"""
    return MOCK_DASHBOARD_SUMMARY


def get_active_alerts() -> list[Alert]:
    """Get list of active alerts"""
    return MOCK_ALERTS


def get_transaction_volume() -> list[TransactionVolume]:
    """Get transaction volume trend data"""
    return MOCK_TRANSACTION_VOLUME


def get_alert_details(alert_id: str) -> AlertDetails:
    """Get detailed alert information"""
    # Return mock data for the requested alert, or default to ALT-788
    return MOCK_ALERT_DETAILS.get(alert_id, MOCK_ALERT_DETAILS["ALT-788"])

