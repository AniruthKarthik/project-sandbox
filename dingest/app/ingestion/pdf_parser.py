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

    def parse(self, file_path: Path) -> ParsedDocument:
        try:
            with fitz.open(str(file_path)) as doc:
                text_content = [page.get_text().strip() for page in doc]

                return ParsedDocument(
                    file_name=file_path.name,
                    format=self.supported_format,
                    page_count=len(doc),
                    text_content=text_content,
                    metadata=dict(doc.metadata),
                )
        except Exception as e:
            raise ParseFailureError(file_path.name, str(e))
