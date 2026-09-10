from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import (
    access,
    assets,
    audit,
    auth,
    recovery,
    resources,
    security,
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "TrustLayer API gateway for identity, access control, "
        "digital assets, and audit services."
    ),
    debug=settings.debug,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

app.include_router(
    access.router,
    prefix="/access",
    tags=["Access Control"],
)

app.include_router(
    assets.router,
    prefix="/assets",
    tags=["Assets"],
)

app.include_router(
    audit.router,
    prefix="/audit",
    tags=["Audit"],
)

app.include_router(
    resources.router,
    prefix="/resources",
    tags=["Resources"],
)

app.include_router(
    security.router,
    prefix="/security",
    tags=["Security"],
)

app.include_router(
    recovery.router,
    prefix="/recovery",
    tags=["Recovery"],
)


@app.get("/", tags=["Health"])
async def root() -> dict:
    return {
        "service": settings.app_name,
        "status": "online",
        "version": settings.app_version,
    }


@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"status": "healthy"}