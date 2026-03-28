"""
Products router: catálogo público (sin Depends de JWT ni middleware de auth).
"""
from typing import List, Optional
from fastapi import APIRouter, Query

from services.product_service import ProductService

router = APIRouter()
_product_service = ProductService()


@router.get("/bestsellers", summary="Top selling products")
async def get_bestsellers(limit: int = Query(8, ge=1, le=50)):
    """
    Products ranked by units sold in paid/shipped orders.
    Falls back to catalog order if there is not enough sales data.
    """
    return _product_service.get_bestsellers(limit=limit)


@router.get("/", summary="List all products")
async def get_products(
    search: Optional[str] = Query(None, description="Search in name and description"),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """
    Retrieve the product catalog with optional search and category filters.
    """
    return _product_service.get_all(search=search, category=category)


@router.get("/categories", summary="List available categories")
async def get_categories():
    """Return a list of all unique product categories."""
    return _product_service.get_categories()


@router.get("/{product_id}", summary="Get product details")
async def get_product(product_id: str):
    """
    Retrieve full details for a single product by its ID.

    Raises 404 if the product is not found.
    """
    return _product_service.get_by_id(product_id)
