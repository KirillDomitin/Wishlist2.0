from fastapi import APIRouter, Depends, File, UploadFile

from app.core.dependencies import get_current_user_id
from app.services.upload_service import UploadService

router = APIRouter(prefix="/api/wishlists")


@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    _: str = Depends(get_current_user_id),
) -> dict[str, str]:
    url = await UploadService.save_image(file)
    return {"url": url}
