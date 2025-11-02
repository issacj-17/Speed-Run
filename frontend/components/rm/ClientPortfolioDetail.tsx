"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Users,
  Briefcase,
  TrendingUp,
  Shield,
  FileText,
  DollarSign,
  Activity,
  Target,
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import TransactionHistory from "./TransactionHistory";
import AdverseMediaFeed from "./AdverseMediaFeed";
import ComplianceStatus from "./ComplianceStatus";

const portfolioData = [
  { name: "Stocks", value: 400000, color: "#1E40AF" },
  { name: "Bonds", value: 300000, color: "#3B82F6" },
  { name: "Real Estate", value: 200000, color: "#93C5FD" },
  { name: "Commodities", value: 100000, color: "#BFDBFE" },
];

const performanceData = [
    { month: "Jan", value: 10000 },
    { month: "Feb", value: 12000 },
    { month: "Mar", value: 8000 },
    { month: "Apr", value: 15000 },
    { month: "May", value: 18000 },
    { month: "Jun", value: 22000 },
];

export default function ClientPortfolioDetail({ client }: { client: any }) {
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

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left Column */}
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users /> Client Profile
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p><strong>ID:</strong> {client.client_id}</p>
            <p><strong>Name:</strong> {client.full_name}</p>
            <p><strong>Account Type:</strong> {client.account_type}</p>
            <p><strong>Risk Rating:</strong> <Badge className={getRiskColor(client.risk_rating)}>{client.risk_rating}</Badge></p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Briefcase /> Portfolio Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p><strong>Total Value:</strong> $1,000,000</p>
            <p><strong>YTD Return:</strong> +5.2%</p>
            <p><strong>Risk Profile:</strong> Growth</p>
          </CardContent>
        </Card>
        <TransactionHistory transactions={client.transactionHistory} />
        <AdverseMediaFeed media={client.adverseMedia} />
      </div>

      {/* Right Column */}
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp /> Asset Allocation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={portfolioData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} fill="#8884d8">
                  {portfolioData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <ComplianceStatus status={client.complianceStatus} />
      </div>
    </div>
  );
}
