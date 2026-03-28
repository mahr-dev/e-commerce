"""
Entrada que usa Vercel para FastAPI (expone la variable `app`).

Root Directory del proyecto en Vercel: service/backend

No uses outputDirectory: "public" en vercel.json para este API: convierte el
deploy en solo estático y la función Python no se publica.
"""
from main import app  # noqa: F401
