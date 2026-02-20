from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api import faq_router
from app.db.base import Base
from app.db.import_models import *  # noqa: F401,F403
from app.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="FAQ Service", version="0.1.0", lifespan=lifespan)
app.include_router(faq_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)