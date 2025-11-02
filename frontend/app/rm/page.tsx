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
import { ArrowLeft, Users, AlertTriangle, FileText, Upload, Search } from "lucide-react";
import { mockClients } from "@/lib/mock-data";
import LeadTimeRecommendation from "@/components/rm/LeadTimeRecommendation";
import PriorityClientsWidget from "@/components/rm/PriorityClientsWidget";
import DocumentUpload from "@/components/rm/DocumentUpload";

export default function RMDashboard() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");

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

  const filteredClients = mockClients.filter((client) =>
    client.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    client.client_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalClients = mockClients.length;
  const pendingReviews = mockClients.filter((c) => c.kyc_status === "under_review").length;
  const totalAlerts = mockClients.reduce((sum, c) => sum + c.alerts, 0);

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

        {/* Priority Clients Widget */}
        <div className="mb-6">
          <PriorityClientsWidget clients={mockClients} />
        </div>

        {/* Lead Time Recommendation Section */}
        <div className="mb-6">
          <LeadTimeRecommendation />
        </div>

        {/* Document Upload Section */}
        <div className="mb-6">
          <DocumentUpload clients={mockClients} />
        </div>

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
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => router.push(`/rm/${client.client_id}`)}
                      >
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

