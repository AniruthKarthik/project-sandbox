from abc import ABC, abstractmethod
from pathlib import Path
from app.models.document import FileFormat, ParsedDocument


class BaseParser(ABC):

    @property
    @abstractmethod
    def supported_format(self) -> FileFormat:
        pass

    @property
    @abstractmethod
    def supported_extensions(self) -> set[str]:
        pass

    @abstractmethod
    def parse(self, filePath: Path) -> ParsedDocument:
        pass

    def can_handle(self, extension: str) -> bool:
        return extension.lower().lstrip(".") in self.supported_extensions
