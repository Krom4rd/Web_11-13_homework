from fastapi import FastAPI

from .routers import contacts


app = FastAPI()

app.include_router(contacts.router, prefix="/api")

@app.get("/")
async def root():
    return {
        "massege":"Hello fastAPI",
        "status": "OK",
        "error": None
        }