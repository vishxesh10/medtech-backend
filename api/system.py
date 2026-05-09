from __future__ import annotations

from fastapi import APIRouter

from config import get_settings

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/version")
def version():
    s = get_settings()
    return {"name": s.app_name, "version": s.app_version}

