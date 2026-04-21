import { useRef, useState, type DragEvent, type ChangeEvent } from "react";

interface DropZoneProps {
  onFile: (file: File) => void;
  disabled?: boolean;
}

const ACCEPTED = ".pdf,.docx,.xlsx,.xls,.pptx,.csv";

export const DropZone = ({ onFile, disabled }: DropZoneProps) => {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) onFile(file);
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFile(file);
  };

  return (
    <div
      className={`dropzone ${dragging ? "dropzone--active" : ""} ${disabled ? "dropzone--disabled" : ""}`}
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        style={{ display: "none" }}
        onChange={handleChange}
        disabled={disabled}
      />
      <div className="dropzone__icon">⬆</div>
      <p className="dropzone__text">
        {dragging ? "Drop it" : "Drag a file here or click to browse"}
      </p>
      <p className="dropzone__hint">PDF · DOCX · XLSX · PPTX · CSV</p>
    </div>
  );
};
