from pydantic import BaseModel
from typing import List, Dict


# Auth schemas 

class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Bill schemas

class ItemCreate(BaseModel):
    name: str
    price: float
    consumers: List[str]


class ItemizedBillCreate(BaseModel):
    title: str
    tip_percentage: float
    items: List[ItemCreate]


class BillResponse(BaseModel):
    id: int
    title: str
    total_amount: float
    tip_percentage: float
    owner_id: int

    class Config:
        from_attributes = True


class ItemizedBillResponse(BaseModel):
    bill_id: int
    title: str
    grand_total: float
    shares: Dict[str, float]