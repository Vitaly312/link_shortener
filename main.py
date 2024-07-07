from fastapi import FastAPI
from routers import router
from contextlib import asynccontextmanager
from database.database import init_models


@asynccontextmanager
async def lifespan(app):
    await init_models()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
