import pandas as pd
from pathlib import Path
from app.ingestion.base import BaseParser
from app.models.document import FileFormat, ParsedDocument
from app.core.exceptions import ParseFailureError


class ExcelParser(BaseParser):
    @property
    def supported_format(self) -> FileFormat:
        return FileFormat.EXCEL

    @property
    def supported_extensions(self) -> set[str]:
        return {"xls", "xlsx"}

    def parse(self, filePath: Path) -> ParsedDocument:
        try:
            xlFile = pd.ExcelFile(filePath)
            sheetsData = {}

            for sheet in xlFile.sheet_names:
                df = pd.read_excel(filePath, sheet_name=sheet)
                sheetsData[sheet] = df.to_dict(orient="records")

            return ParsedDocument(
                fileName=filePath.name,
                format=self.supported_format,
                pageCount=len(xlFile.sheet_names),
                sheets=sheetsData,
                metadata={"sheet_names": xlFile.sheet_names},
            )
        except Exception as e:
            raise ParseFailureError(filePath.name, str(e))
