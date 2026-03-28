"""
Punto de entrada para Vercel: expone la instancia `app` de FastAPI del backend.
"""
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent / "service" / "backend"
sys.path.insert(0, str(_BACKEND))

from main import app  # noqa: E402
