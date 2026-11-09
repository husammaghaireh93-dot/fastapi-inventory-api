"""
Inventory endpoints: Items CRUD, Stock adjustments, Categories, Stats.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from ..schemas import (
    ItemCreate, ItemUpdate, ItemResponse, StockAdjustment,
    CategoryCreate, CategoryResponse, InventoryStats
)
from ..auth import get_current_user
from .. import crud

router = APIRouter(tags=["Inventory"])

@router.get("/stats", response_model=InventoryStats)
def read_inventory_stats():
    return crud.get_stats()

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories():
    return crud.get_categories()

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(req: CategoryCreate, user: dict = Depends(get_current_user)):
    cat_id = crud.create_category(req.name, req.description)
    if not cat_id:
        raise HTTPException(status_code=400, detail="Category name already exists")
    return {"id": cat_id, "name": req.name, "description": req.description}

@router.get("/items", response_model=List[ItemResponse])
def list_items(category_id: Optional[int] = None, search: Optional[str] = None, skip: int = 0, limit: int = 100):
    return crud.get_items(category_id=category_id, search=search, skip=skip, limit=limit)

@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(req: ItemCreate, user: dict = Depends(get_current_user)):
    item_id = crud.create_item(
        sku=req.sku,
        name=req.name,
        price=req.price,
        quantity=req.quantity,
        category_id=req.category_id,
        reorder_threshold=req.reorder_threshold or 5
    )
    if not item_id:
        raise HTTPException(status_code=400, detail="Item with this SKU already exists")
    item = crud.get_item_by_id(item_id)
    return item

@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    item = crud.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, req: ItemUpdate, user: dict = Depends(get_current_user)):
    fields = {k: v for k, v in req.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    ok = crud.update_item(item_id, fields)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found or update failed")
    return crud.get_item_by_id(item_id)

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, user: dict = Depends(get_current_user)):
    ok = crud.delete_item(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Item not found")
    return None

@router.post("/items/{item_id}/adjust-stock")
def adjust_item_stock(item_id: int, req: StockAdjustment, user: dict = Depends(get_current_user)):
    res = crud.adjust_stock(item_id, req.change_amount, req.reason or "Adjustment")
    if not res:
        raise HTTPException(status_code=400, detail="Stock adjustment invalid: item not found or insufficient stock")
    return res
