import type { ParsedDocument } from "../types/document";

const BASE = "/api";

export const uploadFile = async (file: File): Promise<ParsedDocument> => {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${BASE}/ingest/upload`, {
    method: "POST",
    body: form,
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail ?? "Upload failed");
  }

  return data as ParsedDocument;
};

export const getSupportedFormats = async (): Promise<string[]> => {
  const res = await fetch(`${BASE}/ingest/formats`);
  const data = await res.json();
  return data.supported_extensions as string[];
};
