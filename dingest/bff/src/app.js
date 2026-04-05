const app = express();

app.use(cors());
app.use(morgan("dev"));
app.use(express.json());

app.use("/api/ingest", ingestRouter);
app.use("/api/health", healthRouter);

app.use((req, res) => {
  res.status(404).json({
    error: "NotFound",
    detail: `Route ${req.method} ${req.path} does not exist`,
  });
});

app.use(errorHandler);
module.exports = app;
