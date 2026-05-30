export type AgentName =
  | "planner"
  | "supervisor"
  | "engineer"
  | "reviewer"
  | "synthesizer"
  | "fallback";

export type ReviewStatus = "PENDING" | "CHANGES_REQUIRED" | "APPROVED";

export type SSEEventType =
  | "session_id"
  | "agent_start"
  | "agent_complete"
  | "state_update"
  | "stream_chunk"
  | "review_status"
  | "error"
  | "complete";

export interface SSEEvent {
  type: SSEEventType;
  agent?: AgentName;
  message?: string;
  output?: string;
  content?: string;
  state?: ExecutionStateData;
  status?: ReviewStatus;
  report?: string;
  error?: string;
  session_id?: string;
  tokens?: number;
  quality_score?: number;
  iterations?: number;
  execution_id?: string;
}

export interface ExecutionStateData {
  execution_id: string;
  user_input: string;
  plan: string;
  next: string;
  instructions: string;
  current_task: string;
  review_status: ReviewStatus;
  quality_score: number;
  iteration_count: number;
  cost_tokens: number;
  model: string;
  max_iterations: number;
}

export interface AgentStatus {
  name: AgentName;
  label: string;
  emoji: string;
  status: "idle" | "active" | "complete" | "error";
}

export const AGENT_LABELS: Record<AgentName, string> = {
  planner: "Planner",
  supervisor: "Supervisor",
  engineer: "Software Engineer",
  reviewer: "Code Reviewer",
  synthesizer: "Final Synthesizer",
  fallback: "Fallback Handler",
};
