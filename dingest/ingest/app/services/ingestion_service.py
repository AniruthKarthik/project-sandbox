import logging
from pathlib import Path

from app.core.exceptions import ParseFailureError, UnsupportedFormatError
from app.ingestion.factory import ParserFactory
from app.models.document import ParsedDocument

logger = logging.getLogger(__name__)


class IngestionService:
    def ingest(self, file_path: Path) -> ParsedDocument:
        logger.info(
            f"Ingestion started | file={file_path.name} size={file_path.stat().st_size}B"
        )

        try:
            parser = ParserFactory.get_parser(file_path)
            logger.debug(
                f"Parser resolved | file={file_path.name} parser={type(parser).__name__}"
            )

            result = parser.parse(file_path)
            logger.info(
                f"Ingestion succeeded | file={file_path.name} format={result.format} pages={result.page_count}"
            )

            return result

        except (UnsupportedFormatError, ParseFailureError):
            logger.warning(
                f"Ingestion failed (known) | file={file_path.name}", exc_info=True
            )

            raise

        except Exception as exc:
            logger.error(
                f"Ingestion failed (unexpected) | file={file_path.name}", exc_info=True
            )

            raise ParseFailureError(file_path.name, str(exc)) from exc
