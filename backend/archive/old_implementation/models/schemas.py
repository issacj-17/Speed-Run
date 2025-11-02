from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Alert(BaseModel):
    alert_id: str
    priority: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    client: str
    client_id: str
    type: str
    amount: float
    currency: str = "CHF"
    risk_score: int
    status: Literal["pending", "investigating", "resolved"]
    timestamp: datetime
    country: Optional[str] = None
    transaction_type: Optional[str] = None
    counterparty: Optional[str] = None
    purpose: Optional[str] = None
    date: Optional[str] = None


class DashboardSummary(BaseModel):
    total_active_alerts: int
    critical_alerts: int
    pending_cases: int
    avg_resolution_time: float
    resolution_time_change: float
    alerts_by_risk: dict


class TransactionVolume(BaseModel):
    month: str
    volume: int


class AgentFinding(BaseModel):
    agent_name: str
    agent_type: Literal["Regulatory Watcher", "Transaction Analyst", "Document Forensics"]
    priority: Literal["critical", "high", "medium"]
    finding: str
    regulation: Optional[str] = None


class DocumentIssue(BaseModel):
    type: Literal["tampering", "inconsistency", "suspicious"]
    description: str
    page: int


class TransactionHistory(BaseModel):
    month: str
    amount: float


class AlertDetails(Alert):
    agent_findings: List[AgentFinding]
    document_issues: List[DocumentIssue]
    transaction_history: List[TransactionHistory]
    document_url: Optional[str] = None


class AuditLogEntry(BaseModel):
    timestamp: datetime
    user: str
    action: str
    details: str
    alert_id: str


class RemediateResponse(BaseModel):
    success: bool
    message: str

