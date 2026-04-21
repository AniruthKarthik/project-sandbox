require("dotenv").config();

const config = {
  port: parseInt(process.env.PORT || "3000", 10),
  fastApiBaseUrl: process.env.FASTAPI_BASE_URL || "http://localhost:8000",
  maxFileSizeMb: parseInt(process.env.MAX_FILE_SIZE_MB || "20", 10),
  allowedExtensions: ["pdf", "docx", "xlsx", "xls", "pptx", "csv"],
};

module.exports = config;
