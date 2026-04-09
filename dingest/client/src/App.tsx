import { DropZone } from "./components/DropZone";
import { ResultPanel } from "./components/ResultPanel";
import { useUpload } from "./hooks/useUpload";
import "./styles/app.css";

const App = () => {
  const { state, upload, reset } = useUpload();

  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__title">Dingest</h1>
        <p className="app__subtitle">Upload any document — get structured data instantly</p>
      </header>

      <main className="app__main">
        {state.status === "idle" && (
          <DropZone onFile={upload} />
        )}

        {state.status === "uploading" && (
          <div className="status-card">
            <div className="spinner" />
            <p>Parsing document...</p>
          </div>
        )}

        {state.status === "error" && (
          <div className="status-card status-card--error">
            <p className="error-msg">⚠ {state.message}</p>
            <button className="btn btn--primary" onClick={reset}>Try again</button>
          </div>
        )}

        {state.status === "success" && (
          <ResultPanel doc={state.data} onReset={reset} />
        )}
      </main>
    </div>
  );
};

export default App;
