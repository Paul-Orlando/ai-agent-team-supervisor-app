"use client";

import { AgentName, AgentStatus, ReviewStatus, AGENT_LABELS } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const STATUS_EMOJI: Record<AgentStatus["status"], string> = {
  idle: "⏳",
  active: "🔄",
  complete: "✅",
  error: "❌",
};

const REVIEW_BADGE: Record<ReviewStatus, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
  PENDING:           { label: "PENDING",           variant: "secondary" },
  CHANGES_REQUIRED:  { label: "CHANGES REQUIRED",  variant: "destructive" },
  APPROVED:          { label: "APPROVED",           variant: "default" },
};

const AGENT_ORDER: AgentName[] = [
  "planner", "supervisor", "engineer", "reviewer", "synthesizer", "fallback",
];

interface Props {
  statuses: Record<AgentName, AgentStatus["status"]>;
  activeAgent: AgentName | null;
  reviewStatus: ReviewStatus;
  activeMessage: string;
}

export function AgentStatusPanel({ statuses, activeAgent, reviewStatus, activeMessage }: Props) {
  const badge = REVIEW_BADGE[reviewStatus];

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold flex items-center justify-between">
          <span>Agent Status</span>
          <Badge variant={badge.variant}>{badge.label}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {AGENT_ORDER.map((name) => {
          const status = statuses[name] ?? "idle";
          const isActive = name === activeAgent;
          return (
            <div
              key={name}
              className={`flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors ${
                isActive ? "bg-blue-50 dark:bg-blue-950 font-medium" : "text-muted-foreground"
              }`}
            >
              <span className="text-base">{STATUS_EMOJI[status]}</span>
              <span className="flex-1">{AGENT_LABELS[name]}</span>
              {isActive && activeMessage && (
                <span className="text-xs text-blue-600 dark:text-blue-400 truncate max-w-[120px]">
                  {activeMessage}
                </span>
              )}
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
