import { useState, useEffect } from "react";
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

const Value = ({ 
  val, 
  isEditing = false, 
  isDate = false,
  onChange 
}: { 
  val: any; 
  isEditing?: boolean; 
  isDate?: boolean;
  onChange?: (val: string) => void 
}) => {
  if (isEditing && onChange) {
    return (
      <input 
        className="detail-item__input" 
        value={val || ""} 
        onChange={(e) => onChange(e.target.value)}
        placeholder="Not specified"
      />
    );
  }
  return (
    <span className="detail-item__value">
      {val ? (isDate ? formatDate(String(val)) : String(val)) : <em style={{ opacity: 0.4 }}>Not specified</em>}
    </span>
  );
};

export const ResultPanel = ({ doc, onReset }: ResultPanelProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedDoc, setEditedDoc] = useState(doc);
  const [hasSaved, setHasSaved] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    setEditedDoc(doc);
    setHasSaved(false);
  }, [doc]);

  const handleSave = () => {
    console.log("Saving changes:", editedDoc);
    setIsEditing(false);
    setHasSaved(true);
  };

  const handleCancel = () => {
    setEditedDoc(doc);
    setIsEditing(false);
  };

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch("/api/ingest/export", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(editedDoc),
      });

      if (!response.ok) {
        throw new Error("Export failed");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = editedDoc.file_name;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download error:", err);
      alert("Failed to reconstruct and download the file.");
    } finally {
      setIsDownloading(false);
    }
  };

  const updateMetadata = (key: keyof ParsedDocument, value: string) => {
    setEditedDoc(prev => ({ ...prev, [key]: value }));
  };

  const renderViewer = () => {
    switch (editedDoc.format) {
      case "excel":
      case "csv":
        return editedDoc.sheets ? (
          <TableViewer
            sheets={editedDoc.sheets}
            isEditing={isEditing}
            onCellChange={(sheet, i, col, val) => {
              const newSheets = { ...editedDoc.sheets! };
              const newRows = [...newSheets[sheet]];
              newRows[i] = { ...newRows[i], [col]: val };
              newSheets[sheet] = newRows;
              setEditedDoc({ ...editedDoc, sheets: newSheets });
            }}
          />
        ) : null;

      case "pdf":
      case "word":
        return editedDoc.text_content ? (
          <TextViewer
            blocks={editedDoc.text_content}
            label={editedDoc.format === "pdf" ? "Page" : "Paragraph"}
            isEditing={isEditing}
            onBlockChange={(idx, val) => {
              const newBlocks = [...editedDoc.text_content!];
              newBlocks[idx] = val;
              setEditedDoc({
                ...editedDoc,
                text_content: newBlocks,
              });
            }}
          />
        ) : null;

      case "ppt":
        return editedDoc.slides ? (
          <SlideViewer
            slides={editedDoc.slides}
            isEditing={isEditing}
            onSlideChange={(i, field, val) => {
              const newSlides = [...editedDoc.slides!];
              newSlides[i] = { ...newSlides[i], [field]: val };
              setEditedDoc({
                ...editedDoc,
                slides: newSlides,
              });
            }}
          />
        ) : null;

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

        <div className="result-panel__actions">
          {hasSaved && !isEditing && (
            <button 
              className="btn btn--download" 
              onClick={handleDownload}
              disabled={isDownloading}
            >
              <span>⬇</span> {isDownloading ? "Generating..." : "Download Edited Document"}
            </button>
          )}
          
          {isEditing ? (
            <>
              <button className="btn btn--primary" onClick={handleSave}>
                Save Changes
              </button>
              <button className="btn btn--ghost" onClick={handleCancel}>
                Cancel
              </button>
            </>
          ) : (
            <button className="btn btn--ghost" onClick={() => setIsEditing(true)}>
              Edit Document
            </button>
          )}
        </div>
      </header>

      <div className="result-container">
        <main className="result-main">{renderViewer()}</main>

        <aside className="details-sidebar">
          <section className="sidebar-section">
            <h3 className="sidebar-section__title">Document Properties</h3>
            <div className="detail-item">
              <span className="detail-item__label">Title</span>
              <Value 
                val={editedDoc.title} 
                isEditing={isEditing} 
                onChange={(v) => updateMetadata("title", v)} 
              />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Author</span>
              <Value 
                val={editedDoc.author} 
                isEditing={isEditing} 
                onChange={(v) => updateMetadata("author", v)} 
              />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Subject</span>
              <Value 
                val={editedDoc.subject} 
                isEditing={isEditing} 
                onChange={(v) => updateMetadata("subject", v)} 
              />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Keywords</span>
              <Value 
                val={editedDoc.keywords} 
                isEditing={isEditing} 
                onChange={(v) => updateMetadata("keywords", v)} 
              />
            </div>
          </section>

          <section className="sidebar-section">
            <h3 className="sidebar-section__title">System Metadata</h3>
            <div className="detail-item">
              <span className="detail-item__label">Creator</span>
              <Value 
                val={editedDoc.creator} 
                isEditing={isEditing} 
                onChange={(v) => updateMetadata("creator", v)} 
              />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Producer</span>
              <Value 
                val={editedDoc.producer} 
                isEditing={isEditing} 
                onChange={(v) => updateMetadata("producer", v)} 
              />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Created</span>
              <Value val={editedDoc.creation_date} isDate />
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Modified</span>
              <Value val={editedDoc.mod_date} isDate />
            </div>
          </section>

          <section className="sidebar-section">
            <h3 className="sidebar-section__title">File Overview</h3>
            <div className="detail-item">
              <span className="detail-item__label">Filename</span>
              <span className="detail-item__value">{editedDoc.file_name}</span>
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Size</span>
              <span className="detail-item__value">
                {formatFileSize(editedDoc.file_size_bytes)}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-item__label">Format</span>
              <span className="detail-item__value--accent">
                {FORMAT_LABEL[doc.format] ?? doc.format}
              </span>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
};
