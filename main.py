from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root() -> object:
    return {"message": "Hello World"}
