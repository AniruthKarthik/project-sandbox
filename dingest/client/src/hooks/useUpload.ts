import { useState } from "react";
import { uploadFile } from "../services/api";
import type { UploadState } from "../types/document";

export const useUpload = () => {
  const [state, setState] = useState<UploadState>({ status: "idle" });

  const upload = async (file: File) => {
    setState({ status: "uploading" });
    try {
      const data = await uploadFile(file);
      setState({ status: "success", data });
    } catch (err) {
      setState({
        status: "error",
        message: err instanceof Error ? err.message : "Unknown error",
      });
    }
  };

  const reset = () => setState({ status: "idle" });

  return { state, upload, reset };
};
