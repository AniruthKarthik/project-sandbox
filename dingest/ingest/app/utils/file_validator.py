from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings
from app.core.exceptions import FileTooLargeError, UnsupportedFormatError


def validate_upload(file: UploadFile, content: bytes) -> None:
    extension = Path(file.filename).suffix.lstrip(".").lower()

    if extension not in settings.allowed_extensions:
        raise UnsupportedFormatError(extension)

    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise FileTooLargeError(file.filename, size_mb, settings.max_upload_size_mb)
