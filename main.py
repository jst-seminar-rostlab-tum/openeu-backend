from fastapi import FastAPI
from app.api import crawler

app = FastAPI()
app.include_router(crawler.router)

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
