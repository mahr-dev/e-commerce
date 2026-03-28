"""
JSON file handler utility.
Provides thread-safe read/write operations for the JSON-based data store.
"""
import json
import os
from typing import Any, Dict, List

# Resolve the /data directory relative to this file's location
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def read_json(filename: str) -> List[Dict[str, Any]]:
    """
    Read and parse a JSON file from the data directory.

    Args:
        filename: Name of the JSON file (e.g., "products.json").

    Returns:
        Parsed list of records. Returns empty list if file not found.
    """
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Corrupted data file '{filename}': {e}") from e


def write_json(filename: str, data: List[Dict[str, Any]]) -> None:
    """
    Serialize and write data to a JSON file in the data directory.

    Args:
        filename: Name of the JSON file (e.g., "orders.json").
        data: List of records to persist.
    """
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_by_id(filename: str, record_id: str, id_field: str = "id") -> Dict[str, Any] | None:
    """
    Find a single record by its ID field.

    Args:
        filename: JSON file to search.
        record_id: The ID value to match.
        id_field: The key to match against (default: "id").

    Returns:
        Matching record dict, or None if not found.
    """
    records = read_json(filename)
    return next((r for r in records if r.get(id_field) == record_id), None)


def update_record(filename: str, record_id: str, updates: Dict[str, Any], id_field: str = "id") -> Dict[str, Any] | None:
    """
    Update a single record in a JSON file by ID.

    Args:
        filename: JSON file to modify.
        record_id: The ID of the record to update.
        updates: Dict of fields to update.
        id_field: The key to match against (default: "id").

    Returns:
        Updated record, or None if not found.
    """
    records = read_json(filename)
    updated = None
    for record in records:
        if record.get(id_field) == record_id:
            record.update(updates)
            updated = record
            break
    if updated:
        write_json(filename, records)
    return updated
