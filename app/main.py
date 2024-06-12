import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware

from .routes import contacts, auth
from app.conf.config import settings_



app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "massege":"Hello fastAPI",
        "status": "OK",
        "error": None
        }

@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=settings_.redis_host,
                          port=settings_.redis_port,
                          db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


