"""
Base Agent class for all AI agents
Ready for Groq API integration when needed
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_name: str, agent_type: str):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.groq_client = None  # Will be initialized when Groq API is added
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze data and return findings
        
        Args:
            data: Input data for analysis
            
        Returns:
            Dictionary with analysis results
        """
        pass
    
    def _call_groq_api(self, prompt: str, model: str = "llama-3.1-70b-versatile") -> str:
        """
        Call Groq API (placeholder for future implementation)
        
        Args:
            prompt: The prompt to send to the AI
            model: The Groq model to use
            
        Returns:
            AI response text
        """
        # TODO: Implement when Groq API key is available
        # from groq import Groq
        # client = Groq(api_key=settings.groq_api_key)
        # response = client.chat.completions.create(
        #     model=model,
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return response.choices[0].message.content
        
        logger.info(f"Mock AI call for {self.agent_name}")
        return "Mock AI response - Groq API not yet configured"

