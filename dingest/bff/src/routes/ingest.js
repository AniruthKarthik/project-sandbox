const express = require("express");
const upload = require("../middleware/upload");
const {
  forwardFileToPython,
  getSupportedFormats,
  exportDocument,
} = require("../services/pythonProxy");

const router = express.Router();

router.post("/upload", upload.single("file"), async (req, res, next) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        error: "MissingFile",
        detail:
          "No file was uploaded. Send a multipart/form-data request with field name 'file'.",
      });
    }

    const result = await forwardFileToPython(
      req.file.buffer,
      req.file.originalname,
      req.file.mimetype,
    );

    return res.status(200).json(result);
  } catch (err) {
    next(err);
  }
});

router.get("/formats", async (req, res, next) => {
  try {
    const formats = await getSupportedFormats();
    return res.status(200).json(formats);
  } catch (err) {
    next(err);
  }
});

router.post("/export", async (req, res, next) => {
  try {
    const editedDoc = req.body;
    const { data, headers } = await exportDocument(editedDoc);

    // Forward the binary stream back to the frontend
    res.setHeader("Content-Type", headers["content-type"]);
    res.setHeader("Content-Disposition", headers["content-disposition"]);

    res.send(Buffer.from(data));
  } catch (err) {
    next(err);
  }
});

module.exports = router;
