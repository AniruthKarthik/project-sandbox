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

    def parse(self, filePath: Path) -> ParsedDocument:
        try:
            doc = Document(filePath)
            parags = [p.text for p in doc.paragrphs if p.text.strip()]

            return ParsedDocument(
                fileName=filePath.name,
                format=self.supported_format,
                pageCount=None,
                textContent=parags,
                metadata={"paragraph_count)": len(parags)},
            )

        except Exception as e:
            raise ParseFailureError(filePath.name, str(e))
