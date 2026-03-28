from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class FileFormat(str, Enum):
    EXCEL = "excel"
    CSV = "csv"
    PDF = "pdf"
    WORD = "word"
    PPT = "ppt"
    UNKNOWN = "unknown"


class ParsedDocument(BaseModel):
    file_name: str
    format: FileFormat
    page_count: int | None = Field(
        default=None, desciption="Slides,pages,or sheets count"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    sheets: dict[str, list[dict[str, Any]]] | None = None
    text_content: list[str] | None = Field(
        default=None, desciption="List of text blocks - parasm, pgs or Slides"
    )

    class Config:
        usesEnumValues = True
