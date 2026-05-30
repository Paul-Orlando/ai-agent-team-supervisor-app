"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
  content: string;
  activeAgent: string | null;
  isRunning: boolean;
}

export function OutputDisplay({ content, activeAgent, isRunning }: Props) {
  if (!content && !isRunning) {
    return (
      <Card className="flex-1 min-h-[400px]">
        <CardContent className="flex items-center justify-center h-full text-muted-foreground text-sm pt-8">
          Output will appear here once you submit a request.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="flex-1">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold flex items-center gap-2">
          <span>Output</span>
          {isRunning && activeAgent && (
            <span className="text-xs text-blue-500 animate-pulse">
              {activeAgent === "engineer" && "🔄 Engineer writing..."}
              {activeAgent === "reviewer" && "🔄 Reviewer checking..."}
              {activeAgent === "synthesizer" && "🔄 Synthesizing..."}
              {!["engineer", "reviewer", "synthesizer"].includes(activeAgent) &&
                "🔄 Processing..."}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[600px] pr-4">
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content || ""}
            </ReactMarkdown>
          </div>
          {isRunning && (
            <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-0.5" />
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
