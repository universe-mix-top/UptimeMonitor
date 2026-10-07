from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.modules.api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.modules.foreground.foreground import db_controller_connect, db_controller_disconnect
    await db_controller_connect()
    yield
    await db_controller_disconnect()


app = FastAPI(title="UptimeMonitor API", version="1.0.0", lifespan=lifespan)
app.include_router(router)
