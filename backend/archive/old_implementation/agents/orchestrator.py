"""
Agent Orchestrator
Coordinates multiple AI agents and aggregates their findings
"""

from typing import Dict, Any, List
import asyncio
import logging
from .regulatory_watcher import RegulatoryWatcherAgent
from .transaction_analyst import TransactionAnalystAgent
from .document_forensics import DocumentForensicsAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple AI agents for comprehensive analysis"""
    
    def __init__(self):
        self.regulatory_agent = RegulatoryWatcherAgent()
        self.transaction_agent = TransactionAnalystAgent()
        self.document_agent = DocumentForensicsAgent()
    
    async def analyze_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all agents in parallel and aggregate findings
        
        Args:
            alert_data: Complete alert data including transaction and document info
            
        Returns:
            Comprehensive analysis with all agent findings
        """
        logger.info(f"Starting multi-agent analysis for alert {alert_data.get('alert_id')}")
        
        # Run all agents in parallel for faster analysis
        regulatory_task = self.regulatory_agent.analyze(alert_data)
        transaction_task = self.transaction_agent.analyze(alert_data)
        document_task = self.document_agent.analyze(alert_data)
        
        # Wait for all agents to complete
        regulatory_finding, transaction_finding, document_finding = await asyncio.gather(
            regulatory_task,
            transaction_task,
            document_task
        )
        
        # Get detailed document issues
        document_issues = await self.document_agent.analyze_document_issues(alert_data)
        
        # Calculate overall risk score based on findings
        risk_score = self._calculate_risk_score([
            regulatory_finding,
            transaction_finding,
            document_finding
        ])
        
        logger.info(f"Multi-agent analysis complete. Risk score: {risk_score}")
        
        return {
            "alert_id": alert_data.get("alert_id"),
            "risk_score": risk_score,
            "agent_findings": [
                regulatory_finding,
                transaction_finding,
                document_finding
            ],
            "document_issues": document_issues,
            "analysis_complete": True
        }
    
    def _calculate_risk_score(self, findings: List[Dict[str, Any]]) -> int:
        """
        Calculate overall risk score based on agent findings
        
        Args:
            findings: List of findings from all agents
            
        Returns:
            Risk score from 0-100
        """
        priority_scores = {
            "critical": 35,
            "high": 25,
            "medium": 15,
            "low": 5
        }
        
        total_score = sum(
            priority_scores.get(finding.get("priority", "low"), 0)
            for finding in findings
        )
        
        # Normalize to 0-100 scale
        return min(100, total_score)
    
    async def monitor_transaction_stream(self):
        """
        Future implementation: Monitor real-time transaction stream
        Generate alerts automatically when suspicious patterns detected
        """
        logger.info("Transaction monitoring not yet implemented")
        pass

