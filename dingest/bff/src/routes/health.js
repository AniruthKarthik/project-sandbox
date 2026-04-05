const express = require("express");
const { getPythonHealth } = require("../services/pythonProxy");
const router = express.Router();

router.get("/", async (req, res) => {
  let pythonStatus = "unreachable";
  try {
    await getPythonHealth();
    pythonStatus = "ok";
  } catch {
    pythonStatus = "unreachable";
  }

  return res.status(200).json({
    bff: "ok",
    python_service: pythonStatus,
  });
});

module.exports = router;
