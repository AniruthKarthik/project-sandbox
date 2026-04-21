export type FileFormat = "excel" | "csv" | "pdf" | "word" | "ppt" | "unknown";

export interface ParsedDocument {
  file_name: string;
  file_size_bytes: number;
  file_hash: string;
  format: FileFormat;
  page_count: number | null;
  
  // Standard metadata fields
  title: string | null;
  author: string | null;
  subject: string | null;
  keywords: string | null;
  creator: string | null;
  producer: string | null;
  creation_date: string | null;
  mod_date: string | null;
  trapped: string | null;
  encryption: string | null;

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
