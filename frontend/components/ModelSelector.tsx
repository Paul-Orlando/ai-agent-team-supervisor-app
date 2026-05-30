"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
  model: string;
  onChange: (model: string) => void;
  disabled?: boolean;
}

const MODELS = [
  { value: "gpt-4o-mini", label: "GPT-4o Mini (fast, cheap)" },
  { value: "gpt-4o",      label: "GPT-4o (best quality)" },
];

export function ModelSelector({ model, onChange, disabled }: Props) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">⚙️ Model</CardTitle>
      </CardHeader>
      <CardContent>
        <Select value={model} onValueChange={(v) => v && onChange(v)} disabled={disabled}>
          <SelectTrigger className="text-sm">
            <SelectValue placeholder="Select model" />
          </SelectTrigger>
          <SelectContent>
            {MODELS.map((m) => (
              <SelectItem key={m.value} value={m.value}>
                {m.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </CardContent>
    </Card>
  );
}
