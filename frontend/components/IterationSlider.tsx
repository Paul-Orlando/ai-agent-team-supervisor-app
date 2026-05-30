"use client";

import { Slider } from "@/components/ui/slider";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

export function IterationSlider({ value, onChange, disabled }: Props) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold flex justify-between">
          <span>🔢 Max Iterations</span>
          <span className="font-normal text-muted-foreground">{value}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Slider
          min={1}
          max={10}
          step={1}
          value={[value]}
          onValueChange={(vals) => onChange(Array.isArray(vals) ? (vals as number[])[0] : (vals as number))}
          disabled={disabled}
          className="mt-1"
        />
        <div className="flex justify-between text-xs text-muted-foreground mt-1">
          <span>1</span>
          <span>10</span>
        </div>
      </CardContent>
    </Card>
  );
}
