"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Lightbulb, Users, Clock } from "lucide-react";

const mockIssues = [
  {
    issue: "Missing Proof of Address",
    manpower: "1 RM Assistant",
    resources: "Client Outreach Template",
    leadTime: "2 days",
    recommendation: "Contact client immediately using the standard template to request the missing document.",
  },
  {
    issue: "Source of Wealth Verification",
    manpower: "1 Compliance Analyst",
    resources: "Enhanced Due Diligence Checklist",
    leadTime: "5 days",
    recommendation: "Initiate enhanced due diligence and follow the checklist for source of wealth verification.",
  },
  {
    issue: "High-Risk Transaction Flag",
    manpower: "1 Senior Compliance Officer",
    resources: "Internal Investigation Protocol",
    leadTime: "7 days",
    recommendation: "Escalate to a senior compliance officer and follow the internal investigation protocol.",
  },
];

export default function LeadTimeRecommendation() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb /> Ideal Lead Time & Recommendations
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockIssues.map((issue, index) => (
            <div key={index} className="border-b pb-4">
              <h4 className="font-semibold">{issue.issue}</h4>
              <div className="flex items-center gap-4 text-sm text-gray-600 mt-2">
                <span className="flex items-center gap-1"><Users className="h-4 w-4" />{issue.manpower}</span>
                <span className="flex items-center gap-1"><Clock className="h-4 w-4" />{issue.leadTime}</span>
              </div>
              <p className="text-sm mt-2"><strong>Recommendation:</strong> {issue.recommendation}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
