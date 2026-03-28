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

    def parse(self, filePath: Path) -> ParsedDocument:
        try:
            df = pd.read_csv(filePath)
            data = df.to_dict(orient="records")

            return ParsedDocument(
                fileName=filePath.name,
                format=self.supported_format,
                pageCount=1,
                sheets={"default": data},
                metadata={"columns": list(df.columns), "rows": len(df)},
            )

        except Exception as e:
            raise ParseFailureError(filePath.name, str(e))
            pass
