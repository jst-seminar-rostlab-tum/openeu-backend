from fastapi import FastAPI,Request

from app.api.crawler import router as api_crawler
from app.api.meetings import router as api_meetings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(api_meetings)
app.include_router(api_crawler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.middleware("http")
async def dynamic_cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin and origin.endswith("openeu.netlify.app"):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    return await call_next(request)

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
