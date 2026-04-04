import shutil
import tempfile
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import JSONResponse
from app.models.document import ParsedDocument
from app.models.responses import UploadResponse
from app.services.ingestion_service import IngestionService
from app.utils.file_validator import validate_upload

router = APIRouter(prefix="/ingest", tags=["ingestion"])


def get_ingestion_service() -> IngestionService:
    return IngestionService()


@router.post(
    "/upload",
    response_model=ParsedDocument,
    status_code=status.HTTP_200_OK,
    summary="Upload and parse a document",
    description="Accepts PDF, DOCX, XLSX, XLS, PPTX, or CSV. Returns structed ParsedDocument.",
)
async def upload_and_parse(
    file: UploadFile = File(...),
    service: IngestionService = Depends(get_ingestion_service()),
) -> ParsedDocument:
    content = await file.read()
    validate_upload(file, content)

    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        result = service.ingest(tmp_path)
        result.file_name = file.filename
        return result
    finally:
        tmp_path.unlink(missing_ok=True)


@router.get(
    "/formats",
    summary="List supported file formats",
)
def supported_formats() -> dict:
    from app.ingestion.factory import ParserFactory

    return {"supported_extensions": sorted(ParserFactory.supported_extensions())}
