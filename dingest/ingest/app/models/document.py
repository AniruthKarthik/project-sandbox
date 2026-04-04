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
    format: FileFormat
    page_count: int | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)
    sheets: dict[str, list[dict[str, Any]]] | None = None
    text_content: list[str] | None = Field(default=None)

    @property
    def slides(self) -> list[dict[str, Any]]:
        # Pull the structured slide data from metadata
        return self.metadata.get("structured_slides", [])
