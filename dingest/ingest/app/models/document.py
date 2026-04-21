from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class FileFormat(str, Enum):
    EXCEL = "excel"
    CSV = "csv"
    PDF = "pdf"
    WORD = "word"
    PPT = "ppt"
    UNKNOWN = "unknown"


class ParsedDocument(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    file_name: str
    file_size_bytes: int | None = None
    format: FileFormat
    file_hash: str | None = None
    page_count: int | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)
    sheets: dict[str, list[dict[str, Any]]] | None = None
    text_content: list[str] | None = Field(default=None)

    title: str | None = None
    author: str | None = None
    subject: str | None = None
    keywords: str | None = None
    creator: str | None = None
    producer: str | None = None
    creation_date: str | None = None
    mod_date: str | None = None
    trapped: str | None = None
    encryption: str | None = None

    @property
    def slides(self) -> list[dict[str, Any]]:
        # Pull the structured slide data from metadata
        return self.metadata.get("structured_slides", [])
