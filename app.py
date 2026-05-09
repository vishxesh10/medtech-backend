from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth import router as auth_router
from api.prescription import router as prescription_router
from api.system import router as system_router

from config import get_settings
from fastapi import HTTPException
from utils.logging_config import configure_logging
from utils.errors import http_exception_handler, unhandled_exception_handler
from utils.middleware import RequestIdMiddleware

settings = get_settings()
configure_logging()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIdMiddleware)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(system_router)
app.include_router(auth_router)
app.include_router(prescription_router)
