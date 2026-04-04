from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    detail: str


class UploadResponse(BaseModel):
    message: str
    file_name: str
