import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AgentFinding } from "@/lib/api";
import { AlertCircle } from "lucide-react";

interface AgentFindingsProps {
  findings: AgentFinding[];
}

export function AgentFindings({ findings }: AgentFindingsProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "critical":
        return "bg-red-50 border-red-200";
      case "high":
        return "bg-orange-50 border-orange-200";
      case "medium":
        return "bg-yellow-50 border-yellow-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  const getPriorityBadgeVariant = (priority: string) => {
    switch (priority) {
      case "critical":
        return "critical";
      case "high":
        return "high";
      case "medium":
        return "medium";
      default:
        return "default";
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-red-600" />
          <CardTitle className="text-lg">AI Agent Findings</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {findings.map((finding, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg border-2 ${getPriorityColor(finding.priority)}`}
          >
            <div className="flex items-start justify-between mb-3">
              <h4 className="font-semibold text-sm">{finding.agent_name}</h4>
              <Badge variant={getPriorityBadgeVariant(finding.priority) as any}>
                {finding.priority}
              </Badge>
            </div>
            <p className="text-sm font-medium mb-2">{finding.finding}</p>
            {finding.regulation && (
              <p className="text-xs text-muted-foreground italic">
                {finding.regulation}
              </p>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

