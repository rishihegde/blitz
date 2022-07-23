from http import server
import uuid
import contextvars
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app import models
from app.database import SessionLocal, engine
from app.core.helper import helper
from app.core.config import settings
from app.routers import server, peering, network, tf

def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app

models.Base.metadata.create_all(bind=engine)

app = get_application()

request_id_contextvar = contextvars.ContextVar("request_id", default=None)

@app.middleware("http")
async def request_middleware(request, call_next):
    request_id = str(uuid.uuid4())
    request_id_contextvar.set(request_id)
    helper.debug("Request started")

    try:
        return await call_next(request)

    except Exception as ex:
        helper.debug(f"Request failed: {ex}")
        return JSONResponse(content={"success": False}, status_code=500)

    finally:
        assert request_id_contextvar.get() == request_id
        helper.debug("Request ended")


@app.get("/")
async def root():
    return {"message": f"This is {settings.PROJECT_NAME}"}

app.include_router(server.router, prefix=settings.API_VERSION)
app.include_router(network.router, prefix=settings.API_VERSION)
app.include_router(peering.router, prefix=settings.API_VERSION)
app.include_router(tf.router, prefix=settings.API_VERSION)
