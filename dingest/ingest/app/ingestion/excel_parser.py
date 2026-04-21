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
            xl = pd.ExcelFile(file_path, engine="openpyxl")
            wb = xl.book

            sheets_data = {}
            for sheet in xl.sheet_names:
                df = xl.parse(sheet)
                sheets_data[sheet] = df.to_dict(orient="records")

            props = wb.properties

            return ParsedDocument(
                file_name=file_path.name,
                format=self.supported_format,
                page_count=len(xl.sheet_names),
                sheets=sheets_data,
                metadata={
                    "sheet_names": xl.sheet_names,
                },
                title=props.title or None,
                author=props.creator or None,
                subject=props.subject or None,
                keywords=props.keywords or None,
                creator=props.creator or None,
                producer=None,
                creation_date=str(props.created) if props.created else None,
                mod_date=str(props.modified) if props.modified else None,
                encryption=None,
            )

        except Exception as e:
            raise ParseFailureError(file_path.name, str(e))
