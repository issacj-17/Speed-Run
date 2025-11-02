"""
WebSocket endpoint for real-time alert updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)


manager = ConnectionManager()


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for real-time alert updates
    
    Clients connect to receive live notifications when:
    - New alerts are created
    - Alert status changes
    - Critical alerts require attention
    """
    await manager.connect(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to Julius Baer AML Platform",
            "timestamp": "2025-11-01T00:00:00Z"
        })
        
        # Keep connection alive and listen for messages
        while True:
            # Receive messages from client (if any)
            data = await websocket.receive_text()
            
            # Echo back for testing
            await websocket.send_json({
                "type": "echo",
                "message": f"Received: {data}"
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_new_alert(alert_data: dict):
    """
    Broadcast new alert to all connected clients
    
    Args:
        alert_data: Alert information to broadcast
    """
    message = {
        "type": "new_alert",
        "data": alert_data,
        "timestamp": alert_data.get("timestamp")
    }
    await manager.broadcast(message)


async def broadcast_alert_update(alert_id: str, status: str):
    """
    Broadcast alert status update to all connected clients
    
    Args:
        alert_id: ID of the alert
        status: New status
    """
    message = {
        "type": "alert_update",
        "alert_id": alert_id,
        "status": status,
        "timestamp": "2025-11-01T00:00:00Z"
    }
    await manager.broadcast(message)

