from fastapi import FastAPI

from .routes import contacts, auth


app = FastAPI()

app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "massege":"Hello fastAPI",
        "status": "OK",
        "error": None
        }