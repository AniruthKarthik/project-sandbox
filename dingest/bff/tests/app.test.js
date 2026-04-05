const request = require("supertest");
const app = require("../src/app");
const pythonProxy = require("../src/services/pythonProxy");

// Mock the proxy so tests never need FastAPI running
jest.mock("../src/services/pythonProxy");

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

describe("GET /api/health", () => {
  it("returns bff ok and python status", async () => {
    pythonProxy.getPythonHealth.mockResolvedValue({ status: "ok" });

    const res = await request(app).get("/api/health");
    expect(res.status).toBe(200);
    expect(res.body.bff).toBe("ok");
    expect(res.body.python_service).toBe("ok");
  });

  it("reports python_service unreachable when FastAPI is down", async () => {
    pythonProxy.getPythonHealth.mockRejectedValue(new Error("ECONNREFUSED"));

    const res = await request(app).get("/api/health");
    expect(res.status).toBe(200); // BFF itself is still up
    expect(res.body.python_service).toBe("unreachable");
  });
});

// ---------------------------------------------------------------------------
// Formats
// ---------------------------------------------------------------------------

describe("GET /api/ingest/formats", () => {
  it("returns supported extensions from FastAPI", async () => {
    pythonProxy.getSupportedFormats.mockResolvedValue({
      supported_extensions: ["csv", "docx", "pdf", "pptx", "xlsx"],
    });

    const res = await request(app).get("/api/ingest/formats");
    expect(res.status).toBe(200);
    expect(res.body.supported_extensions).toContain("pdf");
  });
});

// ---------------------------------------------------------------------------
// Upload — happy path
// ---------------------------------------------------------------------------

describe("POST /api/ingest/upload", () => {
  const mockParsedDoc = {
    file_name: "test.pdf",
    format: "pdf",
    page_count: 1,
    text_content: ["Hello from test"],
    metadata: {},
    sheets: null,
    slides: null,
  };

  it("forwards file to FastAPI and returns ParsedDocument", async () => {
    pythonProxy.forwardFileToPython.mockResolvedValue(mockParsedDoc);

    const res = await request(app)
      .post("/api/ingest/upload")
      .attach("file", Buffer.from("fake pdf content"), {
        filename: "test.pdf",
        contentType: "application/pdf",
      });

    expect(res.status).toBe(200);
    expect(res.body.format).toBe("pdf");
    expect(res.body.file_name).toBe("test.pdf");
    expect(pythonProxy.forwardFileToPython).toHaveBeenCalledTimes(1);
  });

  // ---------------------------------------------------------------------------
  // Upload — error paths
  // ---------------------------------------------------------------------------

  it("returns 400 when no file is attached", async () => {
    const res = await request(app).post("/api/ingest/upload");
    expect(res.status).toBe(400);
    expect(res.body.error).toBe("MissingFile");
  });

  it("returns 415 for unsupported file type", async () => {
    const res = await request(app)
      .post("/api/ingest/upload")
      .attach("file", Buffer.from("some text"), {
        filename: "test.txt",
        contentType: "text/plain",
      });

    expect(res.status).toBe(415);
    expect(res.body.error).toBe("UnsupportedFormat");
  });

  it("surfaces FastAPI error status and body when Python returns an error", async () => {
    const fastApiError = new Error("FastAPI error");
    fastApiError.isFastApiError = true;
    fastApiError.status = 422;
    fastApiError.body = { error: "ParseFailure", detail: "Corrupt file" };
    pythonProxy.forwardFileToPython.mockRejectedValue(fastApiError);

    const res = await request(app)
      .post("/api/ingest/upload")
      .attach("file", Buffer.from("corrupt"), {
        filename: "bad.pdf",
        contentType: "application/pdf",
      });

    expect(res.status).toBe(422);
    expect(res.body.error).toBe("ParseFailure");
  });
});

// ---------------------------------------------------------------------------
// Unknown route
// ---------------------------------------------------------------------------

describe("Unknown routes", () => {
  it("returns 404 for unregistered paths", async () => {
    const res = await request(app).get("/api/does-not-exist");
    expect(res.status).toBe(404);
    expect(res.body.error).toBe("NotFound");
  });
});
