from pptx import Presentation
from pathlib import Path
from app.ingestion.base import BaseParser
from app.models.document import FileFormat, ParsedDocument
from app.core.exceptions import ParseFailureError


class PPTParser(BaseParser):
    @property
    def supported_format(self) -> FileFormat:
        return FileFormat.PPT

    @property
    def supported_extensions(self) -> set[str]:
        return {"pptx"}

    def parse(self, filePath: Path) -> ParsedDocument:
        try:
            prs = Presentation(filePath)
            slideTexts = []

            for slide in prs.slide:
                textRuns = []
                for shape in slide.shape:
                    if hasattr(shape, "text"):
                        textRuns.append(shape.text)
                slideTexts.append("\n.join(textRuns)")

            return ParsedDocument(
                fileName=filePath.name,
                format=self.supported_format,
                pageCount=len(prs.slides),
                textContent=slideTexts,
                metadata={"slide_count": len(prs.slides)},
            )

        except Exception as e:
            raise ParseFailureError(filePath.name, str(e))
