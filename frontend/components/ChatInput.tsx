"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";

interface Props {
  onSubmit: (value: string) => void;
  onClear: () => void;
  isRunning: boolean;
  onAbort: () => void;
}

export function ChatInput({ onSubmit, onClear, isRunning, onAbort }: Props) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed || isRunning) return;
    onSubmit(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Describe what you want to build or ask about... (Ctrl+Enter to submit)"
        rows={5}
        disabled={isRunning}
        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 resize-none"
      />
      <div className="flex gap-2">
        {isRunning ? (
          <Button variant="destructive" onClick={onAbort} className="flex-1">
            ⏹ Stop
          </Button>
        ) : (
          <Button
            onClick={handleSubmit}
            disabled={!value.trim()}
            className="flex-1"
          >
            ▶ Run Agents
          </Button>
        )}
        <Button variant="outline" onClick={onClear} disabled={isRunning}>
          Clear
        </Button>
      </div>
    </div>
  );
}
