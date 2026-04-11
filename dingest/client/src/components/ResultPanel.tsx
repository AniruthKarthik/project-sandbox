import type { ParsedDocument } from "../types/document";
import { TableViewer } from "./TableViewer";
import { TextViewer } from "./TextViewer";
import { SlideViewer } from "./SlideViewer";

interface ResultPanelProps {
  doc: ParsedDocument;
  onReset: () => void;
}

const FORMAT_LABEL: Record<string, string> = {
  pdf: "PDF Document",
  word: "Word Document",
  excel: "Excel Workbook",
  csv: "CSV File",
  ppt: "PowerPoint",
};

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export const ResultPanel = ({ doc, onReset }: ResultPanelProps) => {
  const renderViewer = () => {
    switch (doc.format) {
      case "excel":
      case "csv":
        return doc.sheets ? <TableViewer sheets={doc.sheets} /> : null;

      case "pdf":
        return doc.text_content ? (
          <TextViewer blocks={doc.text_content} label="Page" />
        ) : null;

      case "word":
        return doc.text_content ? (
          <TextViewer blocks={doc.text_content} label="Paragraph" />
        ) : null;

      case "ppt":
        return doc.slides ? <SlideViewer slides={doc.slides} /> : null;

      default:
        return <p>No viewer available for this format.</p>;
    }
  };

  return (
    <div className="result-panel">
      <header className="result-panel__header">
        <button className="btn btn--ghost" onClick={onReset}>
          <span>←</span> Back to Upload
        </button>
        <div className="badge">{FORMAT_LABEL[doc.format] ?? doc.format}</div>
      </header>

      <div className="result-container">
        <main className="result-main">{renderViewer()}</main>

        <aside className="details-sidebar">
          <section className="sidebar-section">
            <h3 className="sidebar-section__title">File Overview</h3>
            <div className="detail-item">
              <span className="detail-item__label">Filename</span>
              <span className="detail-item__value">{doc.file_name}</span>
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Size</span>
              <span className="detail-item__value">
                {formatFileSize(doc.file_size_bytes)}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Hash (shake_256)</span>
              <span className="detail-item__value">{doc.file_hash}</span>
            </div>
            {doc.page_count != null && (
              <div className="detail-item">
                <span className="detail-item__label">
                  {doc.format === "excel"
                    ? "Sheets"
                    : doc.format === "ppt"
                      ? "Slides"
                      : "Pages"}
                </span>
                <span className="detail-item__value">{doc.page_count}</span>
              </div>
            )}
          </section>

          {Object.keys(doc.metadata).length > 0 && (
            <section className="sidebar-section">
              <h3 className="sidebar-section__title">Extracted Details</h3>
              {Object.entries(doc.metadata).map(([key, value]) => {
                // Skip if the value is too complex for simple display
                if (typeof value === "object" && value !== null) return null;
                return (
                  <div key={key} className="detail-item">
                    <span className="detail-item__label">
                      {key.replace(/_/g, " ")}
                    </span>
                    <span className="detail-item__value">{String(value)}</span>
                  </div>
                );
              })}
            </section>
          )}
        </aside>
      </div>
    </div>
  );
};
