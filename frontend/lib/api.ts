import { SSEEvent } from "./types";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "https://ai-agent-team-supervisor-app-production.up.railway.app";

export async function* streamAgents(
  userInput: string,
  sessionId: string | null,
  model: string,
  maxIterations: number,
  signal: AbortSignal
): AsyncGenerator<SSEEvent> {
  const response = await fetch(`${BACKEND}/run-agents`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_input: userInput,
      session_id: sessionId,
      model,
      max_iterations: maxIterations,
    }),
    signal,
  });

  if (!response.ok) {
    throw new Error(`Backend error: ${response.status} ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const raw = line.slice(6).trim();
        if (!raw || raw === "[DONE]") continue;
        try {
          yield JSON.parse(raw) as SSEEvent;
        } catch {
          // skip malformed lines
        }
      }
    }
  }
}

export async function uploadPdf(
  file: File,
  onProgress?: (pct: number) => void
): Promise<{ chunks: number; filename: string }> {
  const form = new FormData();
  form.append("file", file);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${BACKEND}/upload-pdf`);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`Upload failed: ${xhr.statusText}`));
      }
    };

    xhr.onerror = () => reject(new Error("Network error"));
    xhr.send(form);
  });
}

export function downloadReport(
  sessionId: string,
  format: "md" | "pdf" | "docx"
): void {
  window.open(`${BACKEND}/download-report/${sessionId}/${format}`, "_blank");
}

export async function checkHealth(): Promise<{ status: string; rag_chunks: number }> {
  const res = await fetch(`${BACKEND}/health`);
  return res.json();
}
