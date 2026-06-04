"use client";

import { useState, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { uploadPdf } from "@/lib/api";

interface Props {
  ragChunks: number;
  onChunksUpdated: (count: number) => void;
}

export function PdfUpload({ ragChunks, onChunksUpdated }: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [lastUpload, setLastUpload] = useState<{ name: string; chunks: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are accepted");
      return;
    }
    setError(null);
    setIsUploading(true);
    setProgress(0);
    try {
      const result = await uploadPdf(file, setProgress);
      setLastUpload({ name: file.name, chunks: result.chunks });
      onChunksUpdated(ragChunks + result.chunks);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setIsUploading(false);
      setProgress(0);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold flex justify-between">
          <span>📄 Knowledge Base</span>
          <span className="font-normal text-muted-foreground text-xs">
            {ragChunks} chunk{ragChunks !== 1 ? "s" : ""} loaded
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div
          className={`border-2 border-dashed rounded-md p-4 text-center cursor-pointer transition-colors ${
            isDragging
              ? "border-blue-400 bg-blue-50 dark:bg-blue-950"
              : "border-muted-foreground/30 hover:border-muted-foreground/60"
          }`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={onDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
              e.target.value = "";
            }}
          />
          {isUploading ? (
            <div className="space-y-2">
              <p className="text-xs text-muted-foreground">Uploading… {progress}%</p>
              <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">
              Drop PDF here or click to upload
            </p>
          )}
        </div>

        <p className="mt-2 text-xs text-muted-foreground/70 leading-snug">
          Optional. In your request, mention &ldquo;refer to the uploaded document&rdquo; to direct the agents to use it.
        </p>

        {lastUpload && (
          <p className="mt-2 text-xs text-green-600 dark:text-green-400">
            ✓ {lastUpload.name} — {lastUpload.chunks} chunks added
          </p>
        )}
        {error && (
          <p className="mt-2 text-xs text-red-500">{error}</p>
        )}
      </CardContent>
    </Card>
  );
}
