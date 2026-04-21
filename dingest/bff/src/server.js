const app = require("./app");
const config = require("./config");

app.listen(config.port, () => {
  console.log(`dingest running on http://localhost:${config.port}`);
  console.log(`proxying to FASTAPI at ${config.fastApiBaseUrl}`);
});
