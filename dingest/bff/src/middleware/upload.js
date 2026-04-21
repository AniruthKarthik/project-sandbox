const multer = require("multer");
const path = require("path");
const config = require("../config");

const storage = multer.memoryStorage();

const fileFilter = (req, file, cb) => {
  const ext = path.extname(file.originalname).replace(".", "").toLowerCase();
  if (config.allowedExtensions.includes(ext)) {
    cb(null, true);
  } else {
    cb(
      new Error(
        `Unsupported file type: '.${ext}'. Allowed: ${config.allowedExtensions.join(", ")}`,
      ),
      false,
    );
  }
};

const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: config.maxFileSizeMb * 1024 * 1024,
  },
});

module.exports = upload;
