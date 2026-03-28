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

    def parse(self, file_path: Path) -> ParsedDocument:
        try:
            prs = Presentation(file_path)
            slideTexts = []

            for slide in prs.slide:
                textRuns = []
                for shape in slide.shape:
                    if hasattr(shape, "text"):
                        textRuns.append(shape.text)
                slideTexts.append("\n.join(textRuns)")

            return ParsedDocument(
                file_name=file_path.name,
                format=self.supported_format,
                page_count=len(prs.slides),
                text_content=slideTexts,
                metadata={"slide_count": len(prs.slides)},
            )

        except Exception as e:
            raise ParseFailureError(file_path.name, str(e))
