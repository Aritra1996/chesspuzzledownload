import main  # registers all routes including /
from main import app  # noqa: F401 — Vercel picks up `app` as the ASGI handler
