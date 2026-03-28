"""
Entrada FastAPI para un proyecto Vercel dedicado solo al API.

Expone `api_app` (rutas en la raíz: /products, /auth, …), sin prefijo /api
ni estáticos del Angular.

Uvicorn local: uvicorn app:app --reload --port 8000
(o: uvicorn main:api_app --reload --port 8000)
"""
from main import api_app as app  # noqa: E402
