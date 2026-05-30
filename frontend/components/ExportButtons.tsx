"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { downloadReport } from "@/lib/api";

interface Props {
  sessionId: string | null;
  hasReport: boolean;
}

export function ExportButtons({ sessionId, hasReport }: Props) {
  const disabled = !sessionId || !hasReport;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">📥 Export Report</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={disabled}
          onClick={() => sessionId && downloadReport(sessionId, "md")}
          className="w-full justify-start"
        >
          📝 Download Markdown
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={disabled}
          onClick={() => sessionId && downloadReport(sessionId, "pdf")}
          className="w-full justify-start"
        >
          📄 Download PDF
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={disabled}
          onClick={() => sessionId && downloadReport(sessionId, "docx")}
          className="w-full justify-start"
        >
          📋 Download DOCX
        </Button>
      </CardContent>
    </Card>
  );
}
