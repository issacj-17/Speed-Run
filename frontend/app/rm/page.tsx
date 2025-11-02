"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ArrowLeft, Users, AlertTriangle, FileText, Upload, Search, Loader2 } from "lucide-react";
import { useActiveAlerts, useDashboardSummary } from "@/lib/hooks/useDocuments";
import { config } from "@/lib/config";

// Mock client data
const mockClients = [
  {
    client_id: "CLI-456",
    full_name: "Hans Müller",
    account_type: "Private Banking",
    risk_rating: "high",
    kyc_status: "under_review",
    last_updated: "2024-11-01",
    pending_documents: 2,
    alerts: 3,
  },
  {
    client_id: "CLI-789",
    full_name: "Sophie Chen",
    account_type: "Wealth Management",
    risk_rating: "medium",
    kyc_status: "approved",
    last_updated: "2024-10-28",
    pending_documents: 0,
    alerts: 1,
  },
  {
    client_id: "CLI-234",
    full_name: "Mohammed Al-Rashid",
    account_type: "Private Banking",
    risk_rating: "high",
    kyc_status: "under_review",
    last_updated: "2024-10-30",
    pending_documents: 1,
    alerts: 2,
  },
  {
    client_id: "CLI-567",
    full_name: "Emma Thompson",
    account_type: "Investment Advisory",
    risk_rating: "low",
    kyc_status: "approved",
    last_updated: "2024-10-25",
    pending_documents: 0,
    alerts: 0,
  },
  {
    client_id: "CLI-890",
    full_name: "Carlos Mendoza",
    account_type: "Private Banking",
    risk_rating: "medium",
    kyc_status: "pending_documents",
    last_updated: "2024-10-29",
    pending_documents: 3,
    alerts: 1,
  },
];

export default function RMDashboard() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch data from API (if enabled)
  const { data: alertsData, isLoading: alertsLoading, error: alertsError } = useActiveAlerts();
  const { data: summaryData, isLoading: summaryLoading, error: summaryError } = useDashboardSummary();

  // Determine if we should use backend data or fallback to mock data
  const useBackendData = config.features.USE_BACKEND_API && !alertsError && !summaryError;

  // Use backend data if available, otherwise use mock data
  const clients = useBackendData && alertsData?.alerts
    ? alertsData.alerts.map(alert => ({
        client_id: alert.client_id || "N/A",
        full_name: alert.client_name || "Unknown Client",
        account_type: "Private Banking", // Default value
        risk_rating: alert.risk_score > 0.7 ? "high" : alert.risk_score > 0.4 ? "medium" : "low",
        kyc_status: alert.status === "resolved" ? "approved" : alert.status === "pending" ? "pending_documents" : "under_review",
        last_updated: alert.updated_at || alert.created_at || new Date().toISOString().split('T')[0],
        pending_documents: alert.status === "pending" ? 1 : 0,
        alerts: alert.red_flags?.length || 0,
      }))
    : mockClients;

  const getRiskColor = (rating: string) => {
    switch (rating) {
      case "high":
        return "bg-red-100 text-red-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "low":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "approved":
        return "bg-green-100 text-green-800";
      case "under_review":
        return "bg-blue-100 text-blue-800";
      case "pending_documents":
        return "bg-orange-100 text-orange-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "approved":
        return "Approved";
      case "under_review":
        return "Under Review";
      case "pending_documents":
        return "Pending Docs";
      default:
        return status;
    }
  };

  const filteredClients = clients.filter((client) =>
    client.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    client.client_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalClients = useBackendData && summaryData?.summary?.total_clients
    ? summaryData.summary.total_clients
    : clients.length;

  const pendingReviews = useBackendData && summaryData?.summary?.pending_reviews
    ? summaryData.summary.pending_reviews
    : clients.filter((c) => c.kyc_status === "under_review").length;

  const totalAlerts = useBackendData && summaryData?.summary?.total_alerts
    ? summaryData.summary.total_alerts
    : clients.reduce((sum, c) => sum + c.alerts, 0);

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
              <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">JB</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Relationship Manager Dashboard
                </h1>
                <p className="text-sm text-gray-600">Client Management & Document Upload</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-medium text-sm">TW</span>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Thomas Weber</p>
                <p className="text-xs text-gray-600">Relationship Manager</p>
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

        {/* Welcome Section */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome back, Thomas!</h2>
          <p className="text-gray-600">Manage your client portfolio and upload documents</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Clients
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <Users className="h-8 w-8 text-green-600" />
                <div>
                  <div className="text-3xl font-bold text-gray-900">{totalClients}</div>
                  <div className="text-xs text-gray-600">Active accounts</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">
                Pending Reviews
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <FileText className="h-8 w-8 text-blue-600" />
                <div>
                  <div className="text-3xl font-bold text-gray-900">{pendingReviews}</div>
                  <div className="text-xs text-gray-600">Under compliance review</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">
                Active Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-8 w-8 text-orange-600" />
                <div>
                  <div className="text-3xl font-bold text-gray-900">{totalAlerts}</div>
                  <div className="text-xs text-gray-600">Across all clients</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Document Upload Section */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Upload Client Documents
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-green-500 transition-colors">
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <div className="text-sm text-gray-600 mb-4">
                <p className="font-medium mb-1">Click to upload or drag and drop</p>
                <p className="text-xs">PDF, JPG, PNG up to 10MB</p>
              </div>
              <Button className="bg-green-600 hover:bg-green-700">
                Select Files
              </Button>
            </div>
            <div className="mt-4 text-xs text-gray-500">
              <p>Supported document types: Passport, ID Card, Proof of Address, Bank Statements, Tax Documents</p>
            </div>
          </CardContent>
        </Card>

        {/* Client List */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg">My Clients</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  Manage your client portfolio
                </p>
              </div>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search clients..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Client ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Account Type</TableHead>
                  <TableHead>Risk Rating</TableHead>
                  <TableHead>KYC Status</TableHead>
                  <TableHead>Pending Docs</TableHead>
                  <TableHead>Alerts</TableHead>
                  <TableHead>Last Updated</TableHead>
                  <TableHead>Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredClients.map((client) => (
                  <TableRow key={client.client_id} className="hover:bg-gray-50">
                    <TableCell className="font-medium">{client.client_id}</TableCell>
                    <TableCell>{client.full_name}</TableCell>
                    <TableCell className="text-sm">{client.account_type}</TableCell>
                    <TableCell>
                      <Badge className={getRiskColor(client.risk_rating)}>
                        {client.risk_rating}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(client.kyc_status)}>
                        {getStatusLabel(client.kyc_status)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {client.pending_documents > 0 ? (
                        <Badge variant="destructive">{client.pending_documents}</Badge>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {client.alerts > 0 ? (
                        <Badge variant="destructive" className="gap-1">
                          <AlertTriangle className="h-3 w-3" />
                          {client.alerts}
                        </Badge>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {new Date(client.last_updated).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Button size="sm" variant="outline">
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

