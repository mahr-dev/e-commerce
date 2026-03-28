"""
Normalize text for accent/case-insensitive product search.
"""
import re
import unicodedata
from typing import List, Optional

# Palabras muy comunes que no aportan a la búsqueda (evita ruido tipo "de", "y")
_STOPWORDS_ES = frozenset({
    "de", "la", "el", "los", "las", "y", "en", "un", "una", "unos", "unas",
    "con", "por", "para", "a", "al", "del", "lo", "es", "son", "se",
})


def normalize_text(s: str) -> str:
    """Minúsculas, sin tildes ni diacríticos (á→a, ñ se mantiene como n+n? ñ→n for search)."""
    if not s:
        return ""
    # NFD: separa letras de tildes
    nfkd = unicodedata.normalize("NFD", s)
    without_marks = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return without_marks.lower().replace("ñ", "n").replace("ü", "u")


def search_tokens(query: str) -> List[str]:
    """Parte la consulta en tokens útiles (longitud ≥ 2, sin stopwords)."""
    raw = normalize_text(query.strip())
    parts = [p for p in re.split(r"[\s,.;:/\\-]+", raw) if len(p) >= 2]
    return [p for p in parts if p not in _STOPWORDS_ES]


def product_search_blob(product: dict) -> str:
    """Texto único donde buscar: nombre, descripción y categoría."""
    chunks = [
        product.get("name") or "",
        product.get("description") or "",
        product.get("category") or "",
    ]
    return normalize_text(" ".join(chunks))


def matches_product_search(product: dict, query: Optional[str]) -> bool:
    """
    Coincidencia flexible:
    - Ignora mayúsculas y acentos.
    - La frase completa normalizada puede aparecer como subcadena.
    - Si hay varias palabras, todas deben aparecer (subcadena en el texto),
      así "monitor gaming" exige ambas.
    - "computadora" coincide con "computadoras" (subcadena).
    """
    if not query or not query.strip():
        return True

    blob = product_search_blob(product)
    q_norm = normalize_text(query.strip())

    if not q_norm:
        return True

    # Frase completa
    if q_norm in blob:
        return True

    tokens = search_tokens(query)
    if not tokens:
        return q_norm in blob

    return all(t in blob for t in tokens)
