from fastapi import APIRouter
from models.schemas import TransactionVolume, TransactionHistory
from services.mock_data import get_transaction_volume, MOCK_TRANSACTION_HISTORY

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("/volume", response_model=list[TransactionVolume])
async def get_volume():
    """Get transaction volume trend data"""
    return get_transaction_volume()


@router.get("/history/{client_id}", response_model=list[TransactionHistory])
async def get_history(client_id: str):
    """Get historical transaction data for a client"""
    # In production, this would query the database
    return MOCK_TRANSACTION_HISTORY

