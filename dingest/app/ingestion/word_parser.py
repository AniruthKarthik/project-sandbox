from docx import Document
from pathlib import Path
from app.ingestion.base import BaseParser
from app.models.document import ParsedDocument, FileFormat
from app.core.exceptions import ParseFailureError


class WordParser(BaseParser):
    @property
    def supported_format(self) -> FileFormat:
        return FileFormat.WORD

    @property
    def supported_extensions(self) -> set[str]:
        return {"docx"}

    def parse(self, file_path: Path) -> ParsedDocument:
        try:
            doc = Document(file_path)
            parags = [p.text for p in doc.paragraphs if p.text.strip()]
            headings = [
                {"text": p.text} for p in doc.paragraphs if "Heading" in p.style.name
            ]

            return ParsedDocument(
                file_name=file_path.name,
                format=self.supported_format,
                page_count=None,
                text_content=parags,
                metadata={"paragraph_count": len(parags), "headings": headings},
            )

        except Exception as e:
            raise ParseFailureError(file_path.name, str(e))
