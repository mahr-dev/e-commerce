"""
Punto de entrada para Vercel (FastAPI).

Usar app.py y NO index.py: en Vercel, un archivo index.* en la raíz puede
confundirse con recursos estáticos y servirse como descarga en texto plano
en lugar de ejecutarse como función Python.
"""
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent / "service" / "backend"
sys.path.insert(0, str(_BACKEND))

from main import app  # noqa: E402
