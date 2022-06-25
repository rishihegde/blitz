from http import server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import server, peering, network


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


app = get_application()

app.include_router(server.router, prefix=settings.API_VERSION)
app.include_router(network.router, prefix=settings.API_VERSION)
app.include_router(peering.router, prefix=settings.API_VERSION)

@app.get("/")
async def root():
    return {"message": f"This is {settings.PROJECT_NAME}"}
