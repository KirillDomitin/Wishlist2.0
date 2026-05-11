import uuid
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.exceptions import NotFoundError
from app.repositories.user_repository import UserRepository
from app.schemas.user import AdminUserResponse, AdminUserUpdateRequest

_LOG_DIR = Path("/logs")
_SERVICES = ("user-service", "wishlist-service", "reservation-service")
_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

router = APIRouter(prefix="/api/users/admin", dependencies=[Depends(require_admin)])


@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(db: AsyncSession = Depends(get_db)) -> list[AdminUserResponse]:
    users = await UserRepository(db).get_all()
    return [AdminUserResponse.model_validate(u) for u in users]


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: uuid.UUID,
    data: AdminUserUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> AdminUserResponse:
    updated = await UserRepository(db).update(
        user_id,
        name=data.name,
        email=str(data.email) if data.email else None,
        is_admin=data.is_admin,
    )
    if not updated:
        raise NotFoundError("User not found")
    return AdminUserResponse.model_validate(updated)


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await UserRepository(db).delete_by_id(user_id)
    if not deleted:
        raise NotFoundError("User not found")


@router.get("/logs")
async def get_logs(
    service: str = Query(default="all", description="Service name or 'all'"),
    level: str = Query(default="all", description="Log level filter or 'all'"),
    limit: int = Query(default=200, ge=1, le=2000),
) -> list[dict]:
    level_filter = level.upper() if level != "all" else None
    services = _SERVICES if service == "all" else (service,)

    entries: list[dict] = []
    for svc in services:
        log_file = _LOG_DIR / f"{svc}.log"
        if not log_file.exists():
            continue
        with log_file.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(" | ", maxsplit=4)
                if len(parts) < 5:
                    continue
                timestamp, lvl, svc_name, logger, message = parts
                if level_filter and lvl != level_filter:
                    continue
                entries.append({
                    "timestamp": timestamp,
                    "level": lvl,
                    "service": svc_name,
                    "logger": logger,
                    "message": message,
                })

    entries.sort(key=lambda e: e["timestamp"], reverse=True)
    return entries[:limit]
