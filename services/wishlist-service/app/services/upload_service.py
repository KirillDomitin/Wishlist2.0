import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

_UPLOAD_DIR = Path("/uploads")
_ALLOWED_TYPES: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
}
_MAX_SIZE = 10 * 1024 * 1024  # 10 MB


class UploadService:
    @staticmethod
    async def save_image(file: UploadFile) -> str:
        """Save uploaded image to /uploads/, return public URL path."""
        if file.content_type not in _ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Allowed: JPEG, PNG, GIF, WebP.",
            )

        content = await file.read()
        if len(content) > _MAX_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10 MB.")

        ext = _ALLOWED_TYPES[file.content_type]
        filename = f"{uuid.uuid4()}.{ext}"

        _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        (_UPLOAD_DIR / filename).write_bytes(content)

        return f"/uploads/{filename}"
