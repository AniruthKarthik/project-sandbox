from pathlib import Path

from app.core.exceptions import UnsupportedFormatError
from app.ingestion.base import BaseParser
from app.ingestion.csv_parser import CSVParser
from app.ingestion.pdf_parser import PDFParser
from app.ingestion.excel_parser import ExcelParser
from app.ingestion.word_parser import WordParser
from app.ingestion.ppt_parser import PPTParser


class ParserFactory:
    _PARSERS: list[BaseParser] = [
        PPTParser(),
        ExcelParser(),
        WordParser(),
        CSVParser(),
        PDFParser(),
    ]

    @classmethod
    def get_parser(cls, file_path: Path) -> BaseParser:
        extension = file_path.suffix.lstrip(".").lower()

        for parser in cls._PARSERS:
            if parser.can_handle(extension):
                return parser

        raise UnsupportedFormatError(extension)

    @classmethod
    def supported_extensions(cls) -> set[str]:
        result: set[str] = set()
        for parser in cls._PARSERS:
            result |= parser.supported_extensions
        return result
