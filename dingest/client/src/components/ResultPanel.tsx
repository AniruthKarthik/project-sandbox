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

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return null;

  // Handle PDF format: D:20260318130351Z
  if (dateStr.startsWith("D:")) {
    try {
      const year = dateStr.slice(2, 6);
      const month = dateStr.slice(6, 8);
      const day = dateStr.slice(8, 10);
      const hour = dateStr.slice(10, 12);
      const min = dateStr.slice(12, 14);
      
      const date = new Date(Number(year), Number(month) - 1, Number(day), Number(hour), Number(min));
      return date.toLocaleDateString(undefined, { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  }

  // Handle ISO or standard date strings
  const date = new Date(dateStr);
  if (!isNaN(date.getTime())) {
    return date.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  return dateStr;
};

const Value = ({ val, isDate = false }: { val: any; isDate?: boolean }) => (
  <span className="detail-item__value">
    {val ? (isDate ? formatDate(String(val)) : String(val)) : <em style={{ opacity: 0.4 }}>Not specified</em>}
  </span>
);

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
          {/* Section: Standard Properties */}
          <section className="sidebar-section">
            <h3 className="sidebar-section__title">Document Properties</h3>
            <div className="detail-item">
              <span className="detail-item__label">Title</span>
              <Value val={doc.title} />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Author</span>
              <Value val={doc.author} />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Subject</span>
              <Value val={doc.subject} />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Keywords</span>
              <Value val={doc.keywords} />
            </div>
          </section>

          {/* Section: System Metadata */}
          <section className="sidebar-section">
            <h3 className="sidebar-section__title">System Metadata</h3>
            <div className="detail-item">
              <span className="detail-item__label">Creator</span>
              <Value val={doc.creator} />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Producer</span>
              <Value val={doc.producer} />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Created</span>
              <Value val={doc.creation_date} isDate />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Modified</span>
              <Value val={doc.mod_date} isDate />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Trapped</span>
              <Value val={doc.trapped} />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Encryption</span>
              <Value val={doc.encryption} />
            </div>
          </section>

          {/* Section: File Overview */}
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
          </section>

          {/* Section: Any Extra Metadata */}
          {Object.keys(doc.metadata).length > 0 && (
            <section className="sidebar-section">
              <h3 className="sidebar-section__title">Technical Details</h3>
              {Object.entries(doc.metadata).map(([key, value]) => {
                // Filter out keys already shown as top-level fields
                const excludedKeys = [
                  "title", "author", "subject", "keywords", "creator", 
                  "producer", "creationDate", "modDate", "trapped", 
                  "encryption", "creation_date", "mod_date"
                ];
                
                if (excludedKeys.includes(key)) return null;
                if (typeof value === "object" && value !== null) return null;
                if (value === "" || value === null || value === undefined) return null;

                return (
                  <div key={key} className="detail-item">
                    <span className="detail-item__label">
                      {key.replace(/([A-Z])/g, " $1").replace(/_/g, " ")}
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
