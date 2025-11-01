"use client";

import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { TransactionDetails } from "@/components/investigation/TransactionDetails";
import { DocumentViewer } from "@/components/investigation/DocumentViewer";
import { AgentFindings } from "@/components/investigation/AgentFindings";
import { HistoricalContext } from "@/components/investigation/HistoricalContext";
import { ArrowLeft, FileText } from "lucide-react";
import { mockAlertDetails } from "@/lib/mock-data";

export default function InvestigationPage() {
  const params = useParams();
  const router = useRouter();
  const alertId = params.alertId as string;

  // In production, fetch alert details from API
  const alert = mockAlertDetails;

  const averageAmount = 60000;

  const handleRemediate = () => {
    alert("Alert marked for remediation. Audit trail updated.");
    router.push("/");
  };

  const handleViewAuditTrail = () => {
    alert("Audit trail viewer would open here.");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push("/")}
                className="gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </Button>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-medium text-sm">AR</span>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Ana Rodriguez</p>
                <p className="text-xs text-gray-600">Compliance Officer</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* Page Title */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Investigation Cockpit - Alert {alertId}
          </h1>
          <p className="text-sm text-muted-foreground">
            Comprehensive analysis combining transaction data and document forensics
          </p>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Left Column - Transaction Details */}
          <TransactionDetails alert={alert} />

          {/* Right Column - Document Forensics */}
          <DocumentViewer
            documentUrl={alert.document_url}
            issues={alert.document_issues}
          />
        </div>

        {/* AI Agent Findings */}
        <div className="mb-6">
          <AgentFindings findings={alert.agent_findings} />
        </div>

        {/* Historical Context */}
        <div className="mb-6">
          <HistoricalContext
            data={alert.transaction_history}
            currentAmount={alert.amount}
            averageAmount={averageAmount}
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-4">
          <Button
            size="lg"
            className="bg-gray-900 hover:bg-gray-800"
            onClick={handleRemediate}
          >
            Remediate
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="gap-2"
            onClick={handleViewAuditTrail}
          >
            <FileText className="h-4 w-4" />
            View Audit Trail
          </Button>
        </div>
      </main>
    </div>
  );
}

