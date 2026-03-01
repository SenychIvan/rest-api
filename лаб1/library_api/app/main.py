from fastapi import FastAPI
from app.api.books import router as books_router

from app.db.session import engine
from app.db.base import Base

from fastapi import FastAPI

app = FastAPI(title="Library API")

@app.get("/")
async def root():
    return {"message": "Library API is running", "docs": "/docs"}
app = FastAPI(title="Library API")
app.include_router(books_router)

@app.get("/")
async def root():
    return {"message": "Library API is running. Open /docs"}

@app.on_event("startup")
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)