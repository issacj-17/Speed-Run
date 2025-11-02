"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText, Download, Eye, Calendar } from "lucide-react";

// Mock documents for demonstration
const mockDocuments = [
  {
    id: "doc-1",
    fileName: "passport_scan.pdf",
    documentType: "Passport",
    uploadDate: "2024-10-28",
    status: "verified",
    uploadedBy: "Thomas Weber"
  },
  {
    id: "doc-2",
    fileName: "proof_of_address.pdf",
    documentType: "Proof of Address",
    uploadDate: "2024-10-25",
    status: "verified",
    uploadedBy: "Thomas Weber"
  },
  {
    id: "doc-3",
    fileName: "bank_statement_oct.pdf",
    documentType: "Bank Statement",
    uploadDate: "2024-10-22",
    status: "verified",
    uploadedBy: "Thomas Weber"
  },
];

interface ClientDocumentsProps {
  clientId: string;
}

export default function ClientDocuments({ clientId }: ClientDocumentsProps) {
  // In a real app, this would filter documents by clientId
  const clientDocuments = mockDocuments;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "verified":
        return "bg-green-100 text-green-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "rejected":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const handleView = (docId: string) => {
    window.alert(`Viewing document: ${docId}\n\nIn a real app, this would open the PDF viewer.`);
  };

  const handleDownload = (docId: string, fileName: string) => {
    window.alert(`Downloading: ${fileName}\n\nIn a real app, this would download the file.`);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Uploaded Documents
          <Badge variant="secondary">{clientDocuments.length}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {clientDocuments.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FileText className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No documents uploaded yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {clientDocuments.map((doc) => (
              <div
                key={doc.id}
                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="w-10 h-10 bg-blue-100 rounded flex items-center justify-center flex-shrink-0">
                      <FileText className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold text-sm truncate">{doc.fileName}</h4>
                        <Badge className={getStatusColor(doc.status)} variant="outline">
                          {doc.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 mb-2">{doc.documentType}</p>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(doc.uploadDate).toLocaleDateString()}
                        </span>
                        <span>Uploaded by: {doc.uploadedBy}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleView(doc.id)}
                      className="gap-1"
                    >
                      <Eye className="h-4 w-4" />
                      View
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDownload(doc.id, doc.fileName)}
                      className="gap-1"
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

