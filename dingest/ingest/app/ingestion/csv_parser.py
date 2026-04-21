import pandas as pd
from pathlib import Path
from app.ingestion.base import BaseParser
from app.models.document import FileFormat, ParsedDocument
from app.core.exceptions import ParseFailureError


class CSVParser(BaseParser):
    @property
    def supported_format(self) -> FileFormat:
        return FileFormat.CSV

    @property
    def supported_extensions(self) -> set[str]:
        return {"csv"}

    def parse(self, file_path: Path) -> ParsedDocument:
        try:
            df = pd.read_csv(file_path)
            sheet_key = file_path.stem
            data = df.to_dict(orient="records")

            return ParsedDocument(
                file_name=file_path.name,
                format=self.supported_format,
                page_count=1,
                sheets={sheet_key: data},
                title=None,
                author=None,
                subject=None,
                keywords=None,
                creator=None,
                producer="Dingest CSV parser",
                creation_date=None,
                mod_date=None,
                trapped=None,
                encryption=None,
                metadata={"columns": list(df.columns), "row_count": len(df)},
            )

        except Exception as e:
            raise ParseFailureError(file_path.name, str(e))
            pass
