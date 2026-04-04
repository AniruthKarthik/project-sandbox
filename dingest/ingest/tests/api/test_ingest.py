import io
import csv
import pytest
import pandas as pd
from pathlib import Path
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from main import app

client = TestClient(app)


@pytest.fixture
def pdf_bytes() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(72, 720, "DocuHub API test PDF.")
    c.showPage()
    c.save()
    return buf.getvalue()


@pytest.fixture
def excel_bytes() -> bytes:
    buf = io.BytesIO()
    df = pd.DataFrame({"product": ["Widget"], "price": [9.99]})
    df.to_excel(buf, index=False, sheet_name="Sheet1")
    return buf.getvalue()


@pytest.fixture
def csv_bytes() -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerow({"name": "Aniruth", "age": 19})
    return buf.getvalue().encode()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_supported_formats():
    response = client.get("/ingest/formats")
    assert response.status_code == 200
    data = response.json()
    assert "supported_extensions" in data
    assert "pdf" in data["supported_extensions"]


def test_upload_pdf(pdf_bytes):
    response = client.post(
        "/ingest/upload",
        files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "pdf"
    assert data["file_name"] == "test.pdf"
    assert data["page_count"] == 1
    assert isinstance(data["text_content"], list)


def test_upload_excel(excel_bytes):
    response = client.post(
        "/ingest/upload",
        files={
            "file": (
                "test.xlsx",
                excel_bytes,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "excel"
    assert "Sheet1" in data["sheets"]
    assert data["sheets"]["Sheet1"][0]["product"] == "Widget"


def test_upload_csv(csv_bytes):
    response = client.post(
        "/ingest/upload",
        files={"file": ("test.csv", csv_bytes, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "csv"
    sheets = data["sheets"]
    assert len(sheets) == 1
    rows = list(sheets.values())[0]
    assert rows[0]["name"] == "Aniruth"


def test_upload_unsupported_format():
    response = client.post(
        "/ingest/upload",
        files={"file": ("test.txt", b"some text content", "text/plain")},
    )
    assert response.status_code == 415
    data = response.json()
    assert data["error"] == "UnsupportedFormat"


def test_upload_corrupt_pdf():
    response = client.post(
        "/ingest/upload",
        files={"file": ("corrupt.pdf", b"not a real pdf", "application/pdf")},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ParseFailure"


def test_upload_no_file():
    response = client.post("/ingest/upload")
    assert response.status_code == 422
