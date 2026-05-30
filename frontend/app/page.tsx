"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { ChatInput } from "@/components/ChatInput";
import { AgentStatusPanel } from "@/components/AgentStatusPanel";
import { ExecutionStatePanel } from "@/components/ExecutionStatePanel";
import { OutputDisplay } from "@/components/OutputDisplay";
import { PdfUpload } from "@/components/PdfUpload";
import { ModelSelector } from "@/components/ModelSelector";
import { IterationSlider } from "@/components/IterationSlider";
import { ExportButtons } from "@/components/ExportButtons";
import { streamAgents, checkHealth } from "@/lib/api";
import {
  AgentName,
  AgentStatus,
  ExecutionStateData,
  ReviewStatus,
  SSEEvent,
} from "@/lib/types";
import { Separator } from "@/components/ui/separator";

const DEFAULT_STATUSES = (): Record<AgentName, AgentStatus["status"]> => ({
  planner: "idle",
  supervisor: "idle",
  engineer: "idle",
  reviewer: "idle",
  synthesizer: "idle",
  fallback: "idle",
});

export default function HomePage() {
  const [model, setModel] = useState("gpt-4o-mini");
  const [maxIterations, setMaxIterations] = useState(5);
  const [isRunning, setIsRunning] = useState(false);
  const [outputChunks, setOutputChunks] = useState<string[]>([]);
  const [activeAgent, setActiveAgent] = useState<AgentName | null>(null);
  const [activeMessage, setActiveMessage] = useState("");
  const [agentStatuses, setAgentStatuses] = useState(DEFAULT_STATUSES());
  const [execState, setExecState] = useState<ExecutionStateData | null>(null);
  const [reviewStatus, setReviewStatus] = useState<ReviewStatus>("PENDING");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [hasReport, setHasReport] = useState(false);
  const [ragChunks, setRagChunks] = useState(0);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    checkHealth()
      .then((h) => setRagChunks(h.rag_chunks))
      .catch(() => {});
  }, []);

  const handleEvent = useCallback((event: SSEEvent) => {
    switch (event.type) {
      case "session_id":
        if (event.session_id) setSessionId(event.session_id);
        break;
      case "agent_start":
        if (event.agent) {
          setActiveAgent(event.agent);
          setActiveMessage(event.message ?? "");
          setAgentStatuses((prev) => ({ ...prev, [event.agent!]: "active" }));
        }
        break;
      case "agent_complete":
        if (event.agent) {
          setAgentStatuses((prev) => ({ ...prev, [event.agent!]: "complete" }));
        }
        break;
      case "stream_chunk":
        if (event.content) {
          setOutputChunks((prev) => [...prev, event.content!]);
        }
        break;
      case "state_update":
        if (event.state) {
          setExecState(event.state);
          if (event.state.review_status) {
            setReviewStatus(event.state.review_status as ReviewStatus);
          }
        }
        break;
      case "review_status":
        if (event.status) setReviewStatus(event.status);
        break;
      case "complete":
        setHasReport(true);
        if (event.session_id) setSessionId(event.session_id);
        break;
      case "error":
        setOutputChunks((prev) => [
          ...prev,
          `\n\n**Agent Error:** ${event.message ?? event.error}`,
        ]);
        break;
    }
  }, []);

  const handleSubmit = useCallback(
    async (userInput: string) => {
      setIsRunning(true);
      setOutputChunks([]);
      setAgentStatuses(DEFAULT_STATUSES());
      setActiveAgent(null);
      setActiveMessage("");
      setExecState(null);
      setReviewStatus("PENDING");
      setHasReport(false);

      abortRef.current = new AbortController();

      try {
        const gen = streamAgents(
          userInput,
          null,
          model,
          maxIterations,
          abortRef.current.signal
        );
        for await (const event of gen) {
          handleEvent(event);
        }
      } catch (err: unknown) {
        if (err instanceof Error && err.name !== "AbortError") {
          setOutputChunks((prev) => [...prev, `\n\n**Error:** ${err.message}`]);
        }
      } finally {
        setIsRunning(false);
        setActiveAgent(null);
        setActiveMessage("");
      }
    },
    [model, maxIterations, handleEvent]
  );

  const handleClear = () => {
    setOutputChunks([]);
    setAgentStatuses(DEFAULT_STATUSES());
    setActiveAgent(null);
    setActiveMessage("");
    setExecState(null);
    setReviewStatus("PENDING");
    setSessionId(null);
    setHasReport(false);
  };

  const handleAbort = () => {
    abortRef.current?.abort();
    setIsRunning(false);
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b px-6 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold">AI Agent Team</h1>
          <p className="text-xs text-muted-foreground">
            Supervisor Pattern · Multi-Agent Workflow
          </p>
        </div>
        <span className="text-xs text-muted-foreground">
          {ragChunks} RAG chunk{ragChunks !== 1 ? "s" : ""} loaded
        </span>
      </header>

      <div className="flex h-[calc(100vh-57px)]">
        {/* Left Sidebar */}
        <aside className="w-72 shrink-0 border-r p-4 space-y-4 overflow-y-auto">
          <PdfUpload ragChunks={ragChunks} onChunksUpdated={setRagChunks} />
          <Separator />
          <ModelSelector model={model} onChange={setModel} disabled={isRunning} />
          <IterationSlider value={maxIterations} onChange={setMaxIterations} disabled={isRunning} />
          <Separator />
          <ExportButtons sessionId={sessionId} hasReport={hasReport} />
        </aside>

        {/* Center */}
        <main className="flex-1 flex flex-col p-4 gap-4 overflow-hidden">
          <ChatInput
            onSubmit={handleSubmit}
            onClear={handleClear}
            isRunning={isRunning}
            onAbort={handleAbort}
          />
          <div className="flex-1 overflow-hidden">
            <OutputDisplay
              content={outputChunks.join("")}
              activeAgent={activeAgent}
              isRunning={isRunning}
            />
          </div>
        </main>

        {/* Right Sidebar */}
        <aside className="w-72 shrink-0 border-l p-4 space-y-4 overflow-y-auto">
          <AgentStatusPanel
            statuses={agentStatuses}
            activeAgent={activeAgent}
            reviewStatus={reviewStatus}
            activeMessage={activeMessage}
          />
          <ExecutionStatePanel state={execState} isRunning={isRunning} />
        </aside>
      </div>
    </div>
  );
}
