"""
Entrada Vercel (Root Directory = service/backend).

Solo Python: no uses npm en installCommand de este proyecto.
"""
try:
    from main import api_app as app  # noqa: F401
except ImportError:
    from main import app  # noqa: F401
