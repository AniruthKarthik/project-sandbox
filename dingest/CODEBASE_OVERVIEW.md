# Dingest: The Definitive Technical & Architectural Reference

## 1. Project Mission & Architecture Philosophy

**Dingest** (Document Ingest) is an enterprise-grade document ingestion pipeline designed to extract high-fidelity structured data from diverse file formats. In the modern data landscape, valuable information is often trapped in static, semi-structured documents. Dingest unlocks this data by providing a unified, type-safe API for extraction, normalization, and visualization.

### 1.1 The Three-Tier Design
The system follows a strict separation of concerns, ensuring that each layer can be independently maintained, scaled, and tested. This modularity is key to the project's long-term health.

-   **Layer 1: The Presentation Layer (`/client`)**
    -   *Technology*: React 18, TypeScript, Vite, Vanilla CSS.
    -   *Role*: User interaction, file orchestration, and data visualization. It focuses on responsiveness, accessibility, and high-quality user feedback.
-   **Layer 2: The Orchestration Layer (`/bff`)**
    -   *Technology*: Node.js, Express.
    -   *Role*: Security (CORS, payload limits), API proxying, and error normalization. It provides a stable, public-facing interface for the frontend and shields the internal services.
-   **Layer 3: The Ingestion Layer (`/ingest`)**
    -   *Technology*: Python 3.10+, FastAPI, Pandas, PyMuPDF, python-docx, python-pptx.
    -   *Role*: Deep document analysis, file parsing, and structured data generation. It handles the computationally expensive and library-intensive part of the application.

---

## 2. Exhaustive Project Structure & File Map

Understanding the repository layout is crucial for any developer looking to contribute to Dingest.

### 2.1 Client-Side (React)
-   `src/App.tsx`: The heart of the frontend. Manages the global `UploadStatus` and top-level routing.
-   `src/main.tsx`: Standard React 18 entry point with `StrictMode`.
-   `src/hooks/useUpload.ts`: Encapsulates the logic of the upload lifecycle using a custom state machine.
-   `src/services/api.ts`: Centralized fetch calls to the BFF, handling multipart/form-data.
-   `src/components/DropZone.tsx`: An interactive drag-and-drop area with visual state feedback.
-   `src/components/ResultPanel.tsx`: A router for various visualization components based on document format.
-   `src/components/TextViewer.tsx`: Displays paginated text for PDF/Word documents.
-   `src/components/TableViewer.tsx`: Displays spreadsheets and CSVs in a searchable, scrollable grid.
-   `src/components/SlideViewer.tsx`: Displays PowerPoint slide cards with titles and content.
-   `src/types/document.ts`: TypeScript interfaces ensuring model parity with the Python backend.
-   `src/styles/app.css`: Centralized stylesheet for the entire application, emphasizing a clean, professional aesthetic.

### 2.2 BFF (Node.js)
-   `src/server.js`: The application entry point that boots the Express server on a configurable port.
-   `src/app.js`: Configures global middleware including CORS, Morgan logging, and JSON parsing.
-   `src/routes/ingest.js`: Defines the primary API routes for document ingestion and format querying.
-   `src/routes/health.js`: A health check route used for system monitoring and service discovery.
-   `src/services/pythonProxy.js`: The communication bridge to the internal FastAPI service using Axios.
-   `src/middleware/upload.js`: Multer configuration for secure, memory-based file handling.
-   `src/middleware/errorHandler.js`: Logic for normalizing disparate error types into a unified JSON schema.
-   `src/config.js`: Centralized configuration loader for environment variables.

### 2.3 Ingestion Service (Python)
-   `main.py`: FastAPI entry point with global exception handlers and uvicorn configuration.
-   `app/api/routes/ingest.py`: Core API endpoints for document processing and format listing.
-   `app/services/ingestion_service.py`: Orchestrator that manages the parsing lifecycle (Factory -> Parser -> Result).
-   `app/ingestion/factory.py`: The central registry for selecting the appropriate parser based on file extension.
-   `app/ingestion/base.py`: The Abstract Base Class (ABC) defining the mandatory `parse()` interface.
-   `app/ingestion/pdf_parser.py`: Implementation using `PyMuPDF` (fitz) for high-fidelity PDF text extraction.
-   `app/ingestion/excel_parser.py`: Implementation using `Pandas` and `OpenPyXL` for multi-sheet spreadsheet support.
-   `app/ingestion/word_parser.py`: Implementation using `python-docx` for paragraph-level extraction.
-   `app/ingestion/ppt_parser.py`: Implementation using `python-pptx` for structured slide content extraction.
-   `app/ingestion/csv_parser.py`: Implementation using `Pandas` for robust CSV processing.
-   `app/models/document.py`: Pydantic models for strict structured output validation and serialization.
-   `app/utils/file_validator.py`: Logic for byte-level and extension validation to prevent spoofing.
-   `app/core/config.py`: Configuration using Pydantic Settings for type-safe environment management.
-   `app/core/logging.py`: Centralized logging configuration for structured system logs.

---

## 3. The Lifecycle of an Ingestion Request

Tracing a file's journey from the user's desktop to the final data extraction is the best way to understand the system's control flow.

### 3.1 Step 1: Frontend Capture
The user drags `report.pdf` into `DropZone`. The component manages the browser's native `dragover` (to show a drop target) and `drop` events.

```typescript
// client/src/components/DropZone.tsx
const handleDrop = (e: DragEvent<HTMLDivElement>) => {
  e.preventDefault();
  setDragging(false);
  const file = e.dataTransfer.files[0];
  if (file) onFile(file); // Triggers the upload flow in useUpload
};
```

### 3.2 Step 2: State Management via `useUpload`
The `useUpload` hook immediately transitions the UI to an `uploading` state, which renders a loading spinner.

```typescript
// client/src/hooks/useUpload.ts
export const useUpload = () => {
  const [state, setState] = useState<UploadState>({ status: "idle" });

  const upload = async (file: File) => {
    setState({ status: "uploading" }); // Start spinner
    try {
      const data = await uploadFile(file); // Network call to BFF
      setState({ status: "success", data }); // Show results
    } catch (err) {
      setState({ status: "error", message: err.message }); // Show error card
    }
  };

  return { state, upload, reset: () => setState({ status: "idle" }) };
};
```

### 3.3 Step 3: BFF Interception & Proxying
The request arrives at the BFF. Before reaching the route handler, the `multer` middleware processes the raw bytes.

```javascript
// bff/src/middleware/upload.js
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: config.maxFileSizeMb * 1024 * 1024 }, // Enforce size limits
  fileFilter: (req, file, cb) => {
    const ext = path.extname(file.originalname).replace(".", "").toLowerCase();
    if (config.allowedExtensions.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error(`Unsupported file type: '.${ext}'`), false);
    }
  },
});
```

The `pythonProxy` then forwards this buffer to the internal FastAPI service.

```javascript
// bff/src/services/pythonProxy.js
const forwardFileToPython = async (fileBuffer, originalName, mimetype) => {
  const form = new FormData();
  form.append("file", fileBuffer, { filename: originalName, contentType: mimetype });
  const response = await fastApiClient.post("/ingest/upload", form, {
    headers: form.getHeaders(),
  });
  return response.data;
};
```

### 3.4 Step 4: Python Service Orchestration
FastAPI receives the multipart request. It validates the file and passes it to the `IngestionService`.

```python
# ingest/app/api/routes/ingest.py
@router.post("/upload")
async def upload_and_parse(file: UploadFile = File(...), service: IngestionService = Depends(get_ingestion_service)):
    content = await file.read()
    validate_upload(file, content) # Core validation (size, ext)
    
    # Save to a temporary file for the parsers to read
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        result = service.ingest(tmp_path)
        return result
    finally:
        tmp_path.unlink(missing_ok=True) # Cleanup: Ensure no data leaks on disk
```

### 3.5 Step 5: Parser Selection & Execution
The `IngestionService` uses the `ParserFactory` to select the `PDFParser`. The parser then performs the heavy lifting.

```python
# ingest/app/ingestion/pdf_parser.py
class PDFParser(BaseParser):
    def parse(self, file_path: Path) -> ParsedDocument:
        with fitz.open(str(file_path)) as doc:
            text_content = [page.get_text().strip() for page in doc]
            return ParsedDocument(
                format="pdf",
                page_count=len(doc),
                text_content=text_content,
                metadata=doc.metadata,
                # ... metadata extraction ...
            )
```

---

## 4. Specialized Visualization Components

Dingest doesn't just return data; it provides a tailored viewing experience for each format.

### 4.1 `TextViewer.tsx` (PDF / Word)
Optimized for reading multi-page or multi-paragraph text documents. It renders each block with a label for easy reference.

```typescript
export const TextViewer = ({ blocks, label = "Block" }: TextViewerProps) => {
  return (
    <div className="viewer text-viewer">
      {blocks.map((block, i) => (
        <div key={i} className="text-block">
          <span className="text-block__label">{label} {i + 1}</span>
          <p>{block || <em className="empty">— empty —</em>}</p>
        </div>
      ))}
    </div>
  );
};
```

### 4.2 `TableViewer.tsx` (Excel / CSV)
A robust data grid that handles multiple sheets. It dynamically discovers columns and rows from the JSON structure.

```typescript
export const TableViewer = ({ sheets }: TableViewerProps) => {
  const sheetNames = Object.keys(sheets);
  return (
    <div className="viewer table-viewer">
      {sheetNames.map((name) => {
        const rows = sheets[name];
        const columns = Object.keys(rows[0] || {});
        return (
          <div key={name} className="sheet">
            <h3>{name}</h3>
            <div className="table-wrap">
              <table>
                <thead><tr>{columns.map(c => <th key={c}>{c}</th>)}</tr></thead>
                <tbody>{rows.map((r, i) => <tr key={i}>{columns.map(c => <td key={c}>{String(r[c])}</td>)}</tr>)}</tbody>
              </table>
            </div>
          </div>
        );
      })}
    </div>
  );
};
```

### 4.3 `SlideViewer.tsx` (PowerPoint)
Visualizes PowerPoint presentations as a stack of cards, perfect for reviewing slide summaries.

```typescript
export const SlideViewer = ({ slides }: SlideViewerProps) => {
  return (
    <div className="viewer slide-viewer">
      {slides.map((slide) => (
        <div key={slide.slide_number} className="slide-card">
          <div className="slide-card__number">Slide {slide.slide_number}</div>
          {slide.title && <h3>{slide.title}</h3>}
          <p>{slide.content}</p>
        </div>
      ))}
    </div>
  );
};
```

---

## 5. Data Modeling & System Parity

A core strength of Dingest is the strict parity between the Python backend models and the TypeScript frontend interfaces.

### 5.1 Python (Pydantic Model)
We use Pydantic to ensure that every response from the Ingestion Service is valid and structured correctly.

```python
# ingest/app/models/document.py
class ParsedDocument(BaseModel):
    file_name: str
    format: FileFormat
    page_count: Optional[int]
    text_content: Optional[List[str]] = None
    sheets: Optional[Dict[str, List[Dict[str, Any]]]] = None
    slides: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # Metadata fields (Standardized across formats)
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    mod_date: Optional[str] = None
    trapped: Optional[str] = None
    encryption: Optional[str] = None
    # System identification
    file_size_bytes: int = 0
    file_hash: str = ""
```

### 5.2 TypeScript (Mirror Interface)
This interface ensures that the React components never access a property that doesn't exist, preventing runtime errors.

```typescript
// client/src/types/document.ts
export interface ParsedDocument {
  file_name: string;
  format: "pdf" | "word" | "excel" | "ppt" | "csv";
  page_count?: number;
  text_content?: string[];
  sheets?: Record<string, any[]>;
  slides?: Array<{ slide_number: number; title: string; content: string }>;
  metadata: Record<string, any>;
  title?: string;
  author?: string;
  subject?: string;
  keywords?: string;
  creator?: string;
  producer?: string;
  creation_date?: string;
  mod_date?: string;
  trapped?: string;
  encryption?: string;
  file_size_bytes: number;
  file_hash: string;
}
```

---

## 6. Comprehensive Error Handling Strategy

Dingest follows a "Fail-Fast" and "Graceful Recovery" philosophy.

### 6.1 Multi-Layered Defense
1.  **Browser Layer**: The `accept` attribute on file inputs prevents the selection of obvious junk files.
2.  **BFF Layer**: `multer` rejects files based on extension and size before they ever hit the route logic.
3.  **Python API Layer**: `validate_upload` checks the actual content and configuration settings.
4.  **Parser Layer**: Parsers wrap library-specific calls in `try...except` blocks, throwing custom `ParseFailureError` exceptions.

### 6.2 Error Normalization in BFF
The `errorHandler.js` middleware ensures that whether it's a Node error or a Python error, the React frontend receives a consistent JSON schema.

```javascript
// bff/src/middleware/errorHandler.js
const errorHandler = (err, req, res, next) => {
  if (err.name === "MulterError") {
    return res.status(413).json({ error: "UploadError", detail: err.message });
  }
  if (err.isFastApiError) {
    return res.status(err.status).json(err.body);
  }
  console.error("Internal Error:", err);
  return res.status(500).json({ error: "InternalServerError", detail: "Unexpected error" });
};
```

---

## 7. The Ingest Factory Pattern

The `ParserFactory` is the central brain for selecting the right parsing strategy. It adheres to the **Open/Closed Principle**—you can add new parsers without changing the core factory logic.

```python
# ingest/app/ingestion/factory.py
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
```

---

## 8. Development & Installation Guide

### 8.1 Makefile: The Orchestrator
We provide a powerful `Makefile` to simplify common development tasks.

-   `make install`: Installs dependencies for all three layers.
-   `make start`: Stops any running services and starts the Ingest, BFF, and Client services in parallel, then opens the browser.
-   `make test`: Runs the test suites for all components.
-   `make clean`: Cleans up node_modules, virtual environments, and caches.

### 8.2 Manual Installation (Ubuntu/macOS)
1.  **Ingestion Service**:
    ```bash
    cd ingest
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    python main.py
    ```
2.  **BFF**:
    ```bash
    cd bff
    npm install
    npm start
    ```
3.  **Client**:
    ```bash
    cd client
    npm install
    npm run dev
    ```

### 8.3 Environment Configuration
Ensure you have the following environment variables set:
-   `BFF`: `PORT` (default 3000), `FASTAPI_BASE_URL` (default http://localhost:8000).
-   `Ingest`: `MAX_UPLOAD_SIZE_MB` (default 20).

---

## 9. Performance & Security Considerations

### 9.1 Memory & I/O
-   **Node.js**: Uses memory buffering for file uploads. This is fast but consumes RAM. For files over 50MB, a streaming approach would be required.
-   **Python**: Libraries like `fitz` and `pandas` use highly optimized C/C++ engines under the hood, ensuring that even complex PDF parsing is completed in sub-second times.

### 9.2 Security Auditing
-   **No Persistence**: By default, Dingest does not store files. They exist on disk only for the duration of the `parse()` call and are rigorously deleted in a `finally` block.
-   **Spoofing Protection**: Extension validation is combined with MIME type checks to ensure malicious users don't upload executable files masquerading as PDFs.

---

## 10. Troubleshooting Common Issues

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **"Could not reach Python service"** | FastAPI service is down | Run `make ingest` or check port 8000. |
| **"Upload failed: File too large"** | File exceeds 20MB limit | Adjust `MAX_FILE_SIZE_MB` in `.env`. |
| **"Unsupported file type"** | Extension not in whitelist | Add extension to `config.js` and `config.py`. |
| **BFF port 3000 occupied** | Zombie process | Run `make stop` to kill all related processes. |

---

## 11. The Future Roadmap

-   **OCR Integration**: Using Tesseract or AWS Textract for scanned PDF images.
-   **Asynchronous Tasks**: Transitioning to Celery/Redis for handling very large documents (100+ pages).
-   **Cloud Integration**: Native support for S3/GCS buckets.
-   **Post-Processing**: Adding NLP layers (Entity extraction, Summarization) via LLM integration.

---

## 12. Conclusion

Dingest is a professional-grade document processing platform. By combining the strengths of **React** (State management), **Node.js** (Orchestration), and **Python** (Analysis), it provides a robust foundation for any application that needs to turn documents into actionable insights. The codebase is clean, modular, and ready for enterprise-scale extension.

---
*Version: 2.2.0*
*Last Revised: 2026-04-11*
*Total Lines: 500+*
