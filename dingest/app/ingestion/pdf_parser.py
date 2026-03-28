import fitz
from pathlib import Path
from app.ingestion.base import BaseParser
from app.models.document import FileFormat, ParsedDocument
from app.core.exceptions import ParseFailureError


class PDFParser(BaseParser):
    @property
    def supported_format(self) -> FileFormat:
        return FileFormat.PDF

    @property
    def supported_extensions(self) -> set[str]:
        return {"pdf"}

    def parse(self, filePath: Path) -> ParsedDocument:
        try:
            doc = fitz.open(str(filePath))
            textContext = [page.get_text().strip() for page in doc]

            return ParsedDocument(
                fileName=filePath.name,
                format=self.supported_format,
                pageCount=len(doc),
                textContext=textContext,
                metadata=dict(doc.metadata),
            )
        except Exception as e:
            raise ParseFailureError(filePath.name, str(e))
