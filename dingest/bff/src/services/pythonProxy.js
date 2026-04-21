const axios = require("axios");
const FormData = require("form-data");
const config = require("../config");

const fastApiClient = axios.create({
  baseURL: config.fastApiBaseUrl,
  timeout: 30000,
});

const forwardFileToPython = async (fileBuffer, originalName, mimetype) => {
  const form = new FormData();
  form.append("file", fileBuffer, {
    filename: originalName,
    contentType: mimetype,
  });

  try {
    const response = await fastApiClient.post("/ingest/upload", form, {
      headers: form.getHeaders(),
    });
    return response.data;
  } catch (err) {
    if (err.response) {
      const error = new Error("FastAPI error");
      error.isFastApiError = true;
      error.status = err.response.status;
      error.body = err.response.data;
      throw error;
    }
    throw new Error(
      `Could not reach Python service at ${config.fastApiBaseUrl}. Is it running?`,
    );
  }
};

const getSupportedFormats = async () => {
  const response = await fastApiClient.get("/ingest/formats");
  return response.data;
};

const getPythonHealth = async () => {
  const response = await fastApiClient.get("/health");
  return response.data;
};

const exportDocument = async (editedDoc) => {
  try {
    const response = await fastApiClient.post("/ingest/export", editedDoc, {
      responseType: "arraybuffer", // Important for binary data
    });
    return {
      data: response.data,
      headers: response.headers,
    };
  } catch (err) {
    if (err.response) {
      const error = new Error("FastAPI export error");
      error.status = err.response.status;
      error.body = err.response.data;
      throw error;
    }
    throw new Error(`Could not reach Python service for export.`);
  }
};

module.exports = { 
  forwardFileToPython, 
  getSupportedFormats, 
  getPythonHealth,
  exportDocument
};
