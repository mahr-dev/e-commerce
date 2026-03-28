"""
Product service: catalog browsing and search.
"""
from collections import defaultdict
from typing import List, Optional
from fastapi import HTTPException, status

from utils.file_handler import read_json, find_by_id
from utils.search_text import matches_product_search

_COUNTED_ORDER_STATUSES = frozenset({"paid", "shipped"})


class ProductService:
    """Provides read-only access to the product catalog."""

    def get_all(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[dict]:
        """
        Retrieve all products with optional filtering.

        Args:
            search: Full-text search across name and description.
            category: Filter by product category.

        Returns:
            Filtered list of product dicts.
        """
        products = read_json("products.json")

        if search:
            products = [p for p in products if matches_product_search(p, search)]

        if category:
            products = [
                p for p in products
                if p.get("category", "").lower() == category.lower()
            ]

        return products

    def get_by_id(self, product_id: str) -> dict:
        """
        Retrieve a single product by its ID.

        Raises:
            HTTPException 404: If product is not found.
        """
        product = find_by_id("products.json", product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{product_id}' not found"
            )
        return product

    def get_categories(self) -> List[str]:
        """Return a sorted list of unique product categories."""
        products = read_json("products.json")
        return sorted({p.get("category", "uncategorized") for p in products})

    def get_bestsellers(self, limit: int = 8) -> List[dict]:
        """
        Products with highest sold quantity from paid/shipped orders.
        Each item includes `sold_count` for display.
        """
        orders = read_json("orders.json")
        counts: defaultdict[str, int] = defaultdict(int)
        for order in orders:
            if order.get("status") not in _COUNTED_ORDER_STATUSES:
                continue
            for line in order.get("items") or []:
                pid = line.get("product_id")
                if pid:
                    counts[pid] += int(line.get("quantity") or 0)

        products = read_json("products.json")
        by_id = {p["id"]: p for p in products}
        ranked = sorted(counts.keys(), key=lambda pid: counts[pid], reverse=True)

        out: List[dict] = []
        for pid in ranked[:limit]:
            p = by_id.get(pid)
            if p:
                row = dict(p)
                row["sold_count"] = counts[pid]
                out.append(row)

        if len(out) < limit:
            for p in products:
                if len(out) >= limit:
                    break
                if p["id"] in {x["id"] for x in out}:
                    continue
                row = dict(p)
                row["sold_count"] = counts.get(p["id"], 0)
                out.append(row)

        return out[:limit]
