export type FileFormat = "excel" | "csv" | "pdf" | "word" | "ppt" | "unknown";

export interface ParsedDocument {
  file_name: string;
  file_size_bytes:number;
  format: FileFormat;
  page_count: number | null;
  metadata: Record<string, unknown>;
  sheets: Record<string, Record<string, unknown>[]> | null;
  text_content: string[] | null;
  slides: Slide[] | null;
}

export interface Slide {
  slide_number: number;
  title: string | null;
  content: string;
}

export type UploadState =
  | { status: "idle" }
  | { status: "uploading" }
  | { status: "success"; data: ParsedDocument }
  | { status: "error"; message: string };
