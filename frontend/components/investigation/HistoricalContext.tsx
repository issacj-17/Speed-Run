"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { TransactionHistory } from "@/lib/api";

interface HistoricalContextProps {
  data: TransactionHistory[];
  currentAmount: number;
  averageAmount: number;
}

export function HistoricalContext({
  data,
  currentAmount,
  averageAmount,
}: HistoricalContextProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Historical Context</CardTitle>
        <p className="text-sm text-muted-foreground">6-Month Transaction History</p>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <ReferenceLine
              y={averageAmount}
              stroke="#666"
              strokeDasharray="3 3"
              label="Avg"
            />
            <Bar dataKey="amount" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm font-semibold text-yellow-900">
            Current transaction (CHF {currentAmount.toLocaleString()}) is 250% above
            client&apos;s 6-month average of CHF {averageAmount.toLocaleString()}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

