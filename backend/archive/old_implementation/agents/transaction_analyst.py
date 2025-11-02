"""
Transaction Analyst Agent
Analyzes transaction patterns and detects anomalies
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class TransactionAnalystAgent(BaseAgent):
    """Agent that analyzes transaction patterns"""
    
    def __init__(self):
        super().__init__(
            agent_name="Agent 2: Transaction Analyst",
            agent_type="Transaction Analyst"
        )
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze transaction patterns and detect anomalies
        
        Args:
            data: Transaction data with history
            
        Returns:
            Finding with pattern analysis
        """
        amount = data.get("amount", 0)
        history = data.get("transaction_history", [])
        
        # Calculate average from history
        if history:
            avg_amount = sum(h.get("amount", 0) for h in history) / len(history)
            percentage_above = ((amount - avg_amount) / avg_amount) * 100
            
            if percentage_above > 200:
                return {
                    "agent_name": self.agent_name,
                    "agent_type": self.agent_type,
                    "priority": "high",
                    "finding": f"Amount is {int(percentage_above)}% above client's {len(history)}-month transaction average (CHF {int(avg_amount):,})"
                }
            elif percentage_above > 100:
                return {
                    "agent_name": self.agent_name,
                    "agent_type": self.agent_type,
                    "priority": "medium",
                    "finding": f"Amount is {int(percentage_above)}% above client's average, indicating unusual activity"
                }
        
        return {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "priority": "medium",
            "finding": "Transaction amount is within normal range for this client"
        }
    
    async def analyze_with_groq(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Future implementation with Groq API for advanced pattern detection
        """
        prompt = f"""
        You are a financial transaction analyst specializing in AML pattern detection.
        
        Analyze this transaction:
        - Current Amount: CHF {data.get('amount')}
        - Transaction History: {data.get('transaction_history')}
        - Client Type: {data.get('client')}
        
        Identify any unusual patterns, spikes, or anomalies.
        Consider frequency, timing, and amount variations.
        Provide priority level and detailed analysis.
        """
        
        # response = self._call_groq_api(prompt)
        # Parse and return structured data
        
        return await self.analyze(data)  # Fallback to mock

