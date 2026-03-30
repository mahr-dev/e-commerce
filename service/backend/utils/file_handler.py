"""
JSON file handler utility.
Provides read/write operations for the JSON-based data store.

En Vercel el despliegue es solo lectura salvo /tmp; se usa /tmp/ecommerce-data y se
copian los .json del bundle la primera vez por arranque en frío.
"""
import json
import os
import shutil
import tempfile
from typing import Any, Dict, List

_ROOT = os.path.dirname(os.path.dirname(__file__))
_BUNDLE_DATA_DIR = os.path.join(_ROOT, "data")
_TMP_DATA_DIR = os.path.join(tempfile.gettempdir(), "ecommerce-data")


def _use_tmp_storage() -> bool:
    return bool(os.environ.get("VERCEL"))


def _ensure_runtime_data_dir() -> str:
    if not _use_tmp_storage():
        return _BUNDLE_DATA_DIR

    os.makedirs(_TMP_DATA_DIR, exist_ok=True)
    seeded = os.path.join(_TMP_DATA_DIR, ".seeded_from_bundle")
    if os.path.isfile(seeded):
        return _TMP_DATA_DIR

    try:
        for name in os.listdir(_BUNDLE_DATA_DIR):
            if not name.endswith(".json"):
                continue
            src = os.path.join(_BUNDLE_DATA_DIR, name)
            dst = os.path.join(_TMP_DATA_DIR, name)
            if not os.path.isfile(dst):
                shutil.copy2(src, dst)
    except FileNotFoundError:
        pass

    with open(seeded, "w", encoding="utf-8") as f:
        f.write("ok")
    return _TMP_DATA_DIR


DATA_DIR = _ensure_runtime_data_dir()


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
        Updated record dict, or None if not found.
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
