"use client";

import { ExecutionStateData, ReviewStatus } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

interface Props {
  state: ExecutionStateData | null;
  isRunning: boolean;
}

const REVIEW_COLORS: Record<ReviewStatus, string> = {
  PENDING: "bg-gray-100 text-gray-700",
  CHANGES_REQUIRED: "bg-red-100 text-red-700",
  APPROVED: "bg-green-100 text-green-700",
};

export function ExecutionStatePanel({ state, isRunning }: Props) {
  if (!state) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold">Execution State</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-muted-foreground">
            Submit a request to see live state.
          </p>
        </CardContent>
      </Card>
    );
  }

  const iterPct =
    state.max_iterations > 0
      ? (state.iteration_count / state.max_iterations) * 100
      : 0;

  const scorePct = (state.quality_score / 10) * 100;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold flex items-center justify-between">
          <span>Execution State</span>
          {isRunning && (
            <span className="text-xs text-blue-500 animate-pulse">live</span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-xs">
        {/* Current task */}
        {state.current_task && (
          <div>
            <span className="font-medium text-muted-foreground">Task</span>
            <p className="mt-0.5 text-foreground line-clamp-2">{state.current_task}</p>
          </div>
        )}

        {/* Iterations */}
        <div>
          <div className="flex justify-between mb-1">
            <span className="font-medium text-muted-foreground">Iterations</span>
            <span>
              {state.iteration_count} / {state.max_iterations}
            </span>
          </div>
          <Progress value={iterPct} className="h-1.5" />
        </div>

        {/* Quality score */}
        <div>
          <div className="flex justify-between mb-1">
            <span className="font-medium text-muted-foreground">Quality Score</span>
            <span>{state.quality_score > 0 ? `${state.quality_score}/10` : "—"}</span>
          </div>
          <Progress value={scorePct} className="h-1.5" />
        </div>

        {/* Token usage */}
        <div className="flex justify-between">
          <span className="font-medium text-muted-foreground">Tokens</span>
          <span>{state.cost_tokens.toLocaleString()}</span>
        </div>

        {/* Review status */}
        <div className="flex justify-between items-center">
          <span className="font-medium text-muted-foreground">Review</span>
          <span
            className={`rounded px-2 py-0.5 font-semibold ${
              REVIEW_COLORS[state.review_status as ReviewStatus] ??
              REVIEW_COLORS.PENDING
            }`}
          >
            {state.review_status}
          </span>
        </div>

        {/* Model */}
        <div className="flex justify-between">
          <span className="font-medium text-muted-foreground">Model</span>
          <Badge variant="outline" className="text-xs">{state.model}</Badge>
        </div>
      </CardContent>
    </Card>
  );
}
