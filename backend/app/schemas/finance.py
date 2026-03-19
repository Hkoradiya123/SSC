from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GuestFundRequest(BaseModel):
    match_name: str
    guest_fund: float
    notes: Optional[str] = None


class ManualCreditRequest(BaseModel):
    amount: float
    user_id: Optional[int] = None
    notes: Optional[str] = None


class FinanceTransactionResponse(BaseModel):
    id: int
    user_id: Optional[int]
    transaction_type: str
    amount: float
    category: str
    description: Optional[str]
    reference_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
