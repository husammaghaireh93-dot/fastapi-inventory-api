"""
Pydantic v2 schemas for request and response validation.
"""
from typing import Optional, List
from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class ItemCreate(BaseModel):
    sku: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    category_id: Optional[int] = None
    price: float = Field(..., ge=0.0)
    quantity: int = Field(..., ge=0)
    reorder_threshold: Optional[int] = 5

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = Field(None, ge=0.0)
    quantity: Optional[int] = Field(None, ge=0)
    reorder_threshold: Optional[int] = None

class StockAdjustment(BaseModel):
    change_amount: int
    reason: Optional[str] = "Inventory count adjustment"

class ItemResponse(BaseModel):
    id: int
    sku: str
    name: str
    category_id: Optional[int] = None
    price: float
    quantity: int
    reorder_threshold: int
    created_at: str

class InventoryStats(BaseModel):
    total_items: int
    total_quantity: int
    total_valuation: float
    low_stock_items: int
