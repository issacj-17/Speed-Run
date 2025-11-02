"""
Database service - Currently using in-memory mock data
When ready to use MongoDB, uncomment the MongoDB implementation
"""

import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Mock database service using in-memory data"""
    
    @classmethod
    async def connect_db(cls):
        """Mock connection - no actual database needed"""
        logger.info("Using in-memory mock data (no database required)")

    @classmethod
    async def close_db(cls):
        """Mock close - no actual database to close"""
        logger.info("Mock database service closed")

    @classmethod
    def get_db(cls):
        """Mock get_db - returns None since we're using mock data"""
        return None


db_service = DatabaseService()
