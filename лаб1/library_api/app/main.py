from fastapi import FastAPI

from app.api.books import router as books_router
from app.api.auth import router as auth_router
from app.core.rate_limiter import rate_limit_middleware

app = FastAPI(title="Library API with JWT and Rate Limiter")

app.middleware("http")(rate_limit_middleware)

app.include_router(auth_router)
app.include_router(books_router)