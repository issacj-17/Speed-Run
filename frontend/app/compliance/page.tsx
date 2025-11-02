"use client";

import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { KanbanBoardDnD } from "@/components/compliance/KanbanBoardDnD";
import { DocumentUploadAnalysis } from "@/components/compliance/DocumentUploadAnalysis";
import { ArrowLeft, AlertTriangle, FileWarning, Clock, TrendingUp, Loader2 } from "lucide-react";
import { useActiveAlerts, useDashboardSummary } from "@/lib/hooks/useDocuments";
import { config } from "@/lib/config";

// Mock data for Kanban Board
const mockKanbanCards = [
  {
    review_id: "KYC-2024-001",
    client_name: "Hans Müller",
    client_id: "CLI-456",
    risk_score: 85,
    red_flags_count: 3,
    status: "flagged" as const,
    assigned_officer: "Ana Rodriguez",
    time_in_queue: "2 hours",
    priority: "CRITICAL" as const,
  },
  {
    review_id: "KYC-2024-002",
    client_name: "Sophie Chen",
    client_id: "CLI-789",
    risk_score: 65,
    red_flags_count: 1,
    status: "review" as const,
    assigned_officer: "Ana Rodriguez",
    time_in_queue: "4 hours",
    priority: "HIGH" as const,
  },
  {
    review_id: "KYC-2024-003",
    client_name: "Mohammed Al-Rashid",
    client_id: "CLI-234",
    risk_score: 72,
    red_flags_count: 2,
    status: "flagged" as const,
    assigned_officer: "Ana Rodriguez",
    time_in_queue: "1 day",
    priority: "HIGH" as const,
  },
  {
    review_id: "KYC-2024-004",
    client_name: "Emma Thompson",
    client_id: "CLI-567",
    risk_score: 35,
    red_flags_count: 0,
    status: "new" as const,
    assigned_officer: "Ana Rodriguez",
    time_in_queue: "30 mins",
    priority: "MEDIUM" as const,
  },
  {
    review_id: "KYC-2024-005",
    client_name: "Carlos Mendoza",
    client_id: "CLI-890",
    risk_score: 58,
    red_flags_count: 1,
    status: "review" as const,
    assigned_officer: "Ana Rodriguez",
    time_in_queue: "3 hours",
    priority: "MEDIUM" as const,
  },
  {
    review_id: "KYC-2024-006",
    client_name: "Yuki Tanaka",
    client_id: "CLI-123",
    risk_score: 45,
    red_flags_count: 0,
    status: "new" as const,
    assigned_officer: "Ana Rodriguez",
    time_in_queue: "15 mins",
    priority: "MEDIUM" as const,
  },
  {
    review_id: "KYC-2024-007",
    client_name: "Maria Garcia",
    client_id: "CLI-345",
    risk_score: 28,
    red_flags_count: 0,
    status: "resolved" as const,
    assigned_officer: "Ana Rodriguez",
    time_in_queue: "Completed",
    priority: "LOW" as const,
  },
  {
    review_id: "KYC-2024-008",
    client_name: "Ahmed Hassan",
    client_id: "CLI-678",
    risk_score: 92,
    red_flags_count: 5,
    status: "flagged" as const,
    assigned_officer: "Senior Officer",
    time_in_queue: "6 hours",
    priority: "CRITICAL" as const,
  },
];

export default function ComplianceDashboard() {
  const router = useRouter();

  // Fetch data from API (if enabled)
  const { data: alertsData, isLoading: alertsLoading, error: alertsError } = useActiveAlerts();
  const { data: summaryData, isLoading: summaryLoading, error: summaryError } = useDashboardSummary();

  // Determine if we should use backend data or fallback to mock data
  const useBackendData = config.features.USE_BACKEND_API && !alertsError && !summaryError;

  // Use backend data if available, otherwise use mock data
  const kanbanCards = useBackendData && alertsData?.alerts
    ? alertsData.alerts.map(alert => ({
        review_id: alert.alert_id,
        client_name: alert.client_name || "Unknown Client",
        client_id: alert.client_id || "N/A",
        risk_score: Math.round(alert.risk_score * 100), // Convert to 0-100 scale
        red_flags_count: alert.red_flags?.length || 0,
        status: alert.status as "new" | "review" | "flagged" | "resolved",
        assigned_officer: "Ana Rodriguez",
        time_in_queue: alert.created_at ? new Date().toISOString() : "N/A",
        priority: (alert.severity || "MEDIUM") as "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
      }))
    : mockKanbanCards;

  // Calculate summary stats
  const totalPending = useBackendData && summaryData?.summary?.pending_reviews
    ? summaryData.summary.pending_reviews
    : kanbanCards.filter((r) => r.status === "new" || r.status === "review").length;

  const criticalCases = useBackendData && summaryData?.summary?.critical_alerts
    ? summaryData.summary.critical_alerts
    : kanbanCards.filter((r) => r.priority === "CRITICAL").length;

  const totalRedFlags = useBackendData && summaryData?.summary?.total_red_flags
    ? summaryData.summary.total_red_flags
    : kanbanCards.reduce((sum, r) => sum + r.red_flags_count, 0);

  const avgLeadTime = useBackendData && summaryData?.summary?.avg_lead_time_hours
    ? summaryData.summary.avg_lead_time_hours
    : 3.2;

  // Loading state
  const isLoading = config.features.USE_BACKEND_API && (alertsLoading || summaryLoading);

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
                Back to Home
              </Button>
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">JB</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Compliance Officer Dashboard
                </h1>
                <p className="text-sm text-gray-600">KYC Document Review & Risk Assessment</p>
              </div>
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
        {/* API Status Banner */}
        {config.features.USE_BACKEND_API && (alertsError || summaryError) && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center gap-2 text-yellow-800">
              <AlertTriangle className="h-5 w-5" />
              <div>
                <p className="font-medium">Using Demo Data</p>
                <p className="text-sm">Backend API is unavailable. Displaying mock data for demonstration.</p>
              </div>
            </div>
          </div>
        )}

        {/* Loading Overlay */}
        {isLoading && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center gap-3 text-blue-800">
              <Loader2 className="h-5 w-5 animate-spin" />
              <p className="font-medium">Loading dashboard data...</p>
            </div>
          </div>
        )}

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">
                Pending Reviews
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <Clock className="h-8 w-8 text-yellow-600" />
                <div>
                  <div className="text-3xl font-bold text-gray-900">{totalPending}</div>
                  <div className="text-xs text-gray-600">Awaiting review</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">
                Critical Cases
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <FileWarning className="h-8 w-8 text-red-600" />
                <div>
                  <div className="text-3xl font-bold text-gray-900">{criticalCases}</div>
                  <div className="text-xs text-gray-600">Immediate action</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Red Flags
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-8 w-8 text-orange-600" />
                <div>
                  <div className="text-3xl font-bold text-gray-900">{totalRedFlags}</div>
                  <div className="text-xs text-gray-600">Across all cases</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">
                Avg. Lead Time
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <TrendingUp className="h-8 w-8 text-green-600" />
                <div>
                  <div className="text-3xl font-bold text-gray-900">{avgLeadTime}h</div>
                  <div className="text-xs text-green-600">↓ 18% from last month</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Document Upload & Analysis */}
        <div className="mb-6">
          <DocumentUploadAnalysis />
        </div>

        {/* Business Metrics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Business Impact */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">💰 Business Impact Today</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-muted-foreground">Transactions Enabled</div>
                  <div className="text-3xl font-bold text-green-600">CHF 12.5M</div>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                  <div>
                    <div className="text-xs text-muted-foreground">Cases Approved</div>
                    <div className="text-xl font-semibold">55</div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground">Avg Value/Case</div>
                    <div className="text-xl font-semibold">CHF 227K</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Capacity Planning */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">👥 Capacity & Workload</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Officers</div>
                  <div className="text-2xl font-bold">8</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Cases/Day</div>
                  <div className="text-2xl font-bold">7.5</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Backlog</div>
                  <div className="text-2xl font-bold text-orange-600">45</div>
                </div>
              </div>
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
                <span className="font-medium text-blue-900">💡 Recommendation:</span>
                <span className="text-blue-800"> Hire 2 officers to reduce lead time by 35%</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Kanban Board with Drag & Drop */}
        <div>
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900">KYC Review Board</h2>
            <p className="text-sm text-muted-foreground">
              Drag cards between columns or use quick actions • Click cards to open full review
            </p>
          </div>
          <KanbanBoardDnD cards={mockKanbanCards} />
        </div>
      </main>
    </div>
  );
}

