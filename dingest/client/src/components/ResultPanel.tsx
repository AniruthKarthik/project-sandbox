import type { ParsedDocument } from "../types/document";
import { TableViewer } from "./TableViewer";
import { TextViewer } from "./TextViewer";
import { SlideViewer } from "./SlideViewer";

interface ResultPanelProps {
  doc: ParsedDocument;
  onReset: () => void;
}

const FORMAT_LABEL: Record<string, string> = {
  pdf: "PDF",
  word: "Word Document",
  excel: "Excel Workbook",
  csv: "CSV File",
  ppt: "PowerPoint",
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
      <div className="result-panel__header">
        <div className="result-panel__meta">
          <span className="badge">{FORMAT_LABEL[doc.format] ?? doc.format}</span>
          <span className="filename">{doc.file_name}</span>
          {doc.page_count != null && (
            <span className="page-count">{doc.page_count} {doc.format === "excel" ? "sheet(s)" : doc.format === "ppt" ? "slide(s)" : "page(s)"}</span>
          )}
        </div>
        <button className="btn btn--ghost" onClick={onReset}>
          ← Upload another
        </button>
      </div>
      <div className="result-panel__body">{renderViewer()}</div>
    </div>
  );
};
