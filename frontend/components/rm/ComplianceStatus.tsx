"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ShieldCheck } from "lucide-react";

export default function ComplianceStatus({ status }: { status: any }) {
  const getStatusColor = (value: string) => {
    switch (value) {
      case "Clear":
        return "text-green-600";
      case "Potential Match":
        return "text-orange-600";
      default:
        return "text-gray-800";
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShieldCheck /> Compliance Status
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <p><strong>Sanctions Screen:</strong> <span className={getStatusColor(status.sanctions)}>{status.sanctions}</span></p>
          <p><strong>PEP Screen:</strong> <span className={getStatusColor(status.pep)}>{status.pep}</span></p>
          <p><strong>AML Risk Rating:</strong> <span className={getStatusColor(status.aml)}>{status.aml}</span></p>
        </div>
      </CardContent>
    </Card>
  );
}
