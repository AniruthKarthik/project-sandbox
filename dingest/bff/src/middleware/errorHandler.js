const errorHandler = (err, req, res, next) => {
  if (err.name === "MulterError") {
    return res.status(413).json({
      error: "UploadError",
      detail: err.message,
    });
  }

  if (err.message?.startsWith("Unsupported file type")) {
    return res.status(415).json({
      error: "UnsupportedFormat",
      detail: err.message,
    });
  }

  if (err.isFastApiError) {
    return res.status(err.status).json(err.body);
  }

  console.error("Unhandled error:", err);
  return res.status(500).json({
    error: "InternalServerError",
    detail: "An unexpected error occurred.",
  });
};

module.exports = errorHandler;
