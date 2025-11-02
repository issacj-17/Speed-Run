"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { TrendingUp } from "lucide-react";

export default function TransactionHistory({ transactions }: { transactions: any[] }) {
  const getRiskColor = (risk: string) => {
    switch (risk) {
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
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp /> Recent Transactions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Risk</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {transactions.map((tx, index) => (
              <TableRow key={index}>
                <TableCell>{tx.date}</TableCell>
                <TableCell>{tx.description}</TableCell>
                <TableCell className={tx.amount > 0 ? "text-green-600" : "text-red-600"}>
                  {tx.amount.toLocaleString()}
                </TableCell>
                <TableCell>
                  <Badge className={getRiskColor(tx.risk)}>{tx.risk}</Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
