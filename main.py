from fastapi import FastAPI
from app.api import crawler

app = FastAPI()
app.include_router(crawler.router)

@app.get("/")
async def root() -> object:
    return {"message": "Hello World"}