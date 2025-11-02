"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import ClientPortfolioDetail from "@/components/rm/ClientPortfolioDetail";
import { mockClients } from "@/lib/mock-data";

export default function ClientDetailPage({ params }: { params: { clientId: string } }) {
  const router = useRouter();
  const client = mockClients.find(c => c.client_id === params.clientId);

  if (!client) {
    return <div>Client not found</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push("/rm")}
                className="gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </Button>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Client Portfolio: {client.full_name}
              </h1>
              <p className="text-sm text-gray-600">{client.client_id}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6">
        <ClientPortfolioDetail client={client} />
      </main>
    </div>
  );
}
