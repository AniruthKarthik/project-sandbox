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

    def parse(self, file_path: Path) -> ParsedDocument:
        try:
            xl_file = pd.ExcelFile(file_path)
            sheets_data = {}

            for sheet in xl_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet)
                sheets_data[sheet] = df.to_dict(orient="records")

            return ParsedDocument(
                file_name=file_path.name,
                format=self.supported_format,
                page_count=len(xl_file.sheet_names),
                sheets=sheets_data,
                metadata={"sheet_names": xl_file.sheet_names},
            )
        except Exception as e:
            raise ParseFailureError(file_path.name, str(e))
