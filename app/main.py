from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes.cv_matching import router as cv_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cv_router, prefix=settings.API_PREFIX)