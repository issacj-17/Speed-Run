"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Upload, File, X, CheckCircle, AlertCircle } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface UploadedDocument {
  id: string;
  fileName: string;
  fileSize: number;
  clientId: string;
  clientName: string;
  documentType: string;
  uploadDate: string;
  status: "uploaded" | "processing" | "verified";
}

interface DocumentUploadProps {
  clients: any[];
  onDocumentsUpdate?: (documents: UploadedDocument[]) => void;
}

export default function DocumentUpload({ clients, onDocumentsUpdate }: DocumentUploadProps) {
  const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDocument[]>([]);
  const [selectedClient, setSelectedClient] = useState<string>("");
  const [selectedDocType, setSelectedDocType] = useState<string>("");
  const [isDragging, setIsDragging] = useState(false);

  const documentTypes = [
    "Passport",
    "ID Card",
    "Proof of Address",
    "Bank Statement",
    "Tax Document",
    "Business Registration",
    "Other"
  ];

  const handleFileSelect = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    
    if (!selectedClient || !selectedDocType) {
      alert("Please select a client and document type first");
      return;
    }

    const client = clients.find(c => c.client_id === selectedClient);
    
    Array.from(files).forEach((file) => {
      // Check if file is PDF
      if (file.type !== "application/pdf") {
        alert(`${file.name} is not a PDF file. Please upload PDF files only.`);
        return;
      }

      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert(`${file.name} exceeds 10MB limit`);
        return;
      }

      const newDoc: UploadedDocument = {
        id: `doc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        fileName: file.name,
        fileSize: file.size,
        clientId: selectedClient,
        clientName: client?.full_name || "Unknown Client",
        documentType: selectedDocType,
        uploadDate: new Date().toISOString(),
        status: "uploaded"
      };

      setUploadedDocuments(prev => {
        const updated = [...prev, newDoc];
        onDocumentsUpdate?.(updated);
        return updated;
      });

      // Simulate processing
      setTimeout(() => {
        setUploadedDocuments(prev => 
          prev.map(doc => 
            doc.id === newDoc.id ? { ...doc, status: "verified" as const } : doc
          )
        );
      }, 2000);
    });
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleRemoveDocument = (docId: string) => {
    setUploadedDocuments(prev => {
      const updated = prev.filter(doc => doc.id !== docId);
      onDocumentsUpdate?.(updated);
      return updated;
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "verified":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "processing":
        return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      default:
        return <File className="h-4 w-4 text-blue-600" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Upload Client Documents
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Client and Document Type Selection */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Select Client</label>
            <Select value={selectedClient} onValueChange={setSelectedClient}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a client..." />
              </SelectTrigger>
              <SelectContent>
                {clients.map((client) => (
                  <SelectItem key={client.client_id} value={client.client_id}>
                    {client.full_name} ({client.client_id})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block">Document Type</label>
            <Select value={selectedDocType} onValueChange={setSelectedDocType}>
              <SelectTrigger>
                <SelectValue placeholder="Choose document type..." />
              </SelectTrigger>
              <SelectContent>
                {documentTypes.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Upload Area */}
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging
              ? "border-green-500 bg-green-50"
              : "border-gray-300 hover:border-green-500"
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <div className="text-sm text-gray-600 mb-4">
            <p className="font-medium mb-1">Click to upload or drag and drop</p>
            <p className="text-xs">PDF files only, up to 10MB</p>
          </div>
          <input
            type="file"
            accept=".pdf,application/pdf"
            multiple
            onChange={(e) => handleFileSelect(e.target.files)}
            className="hidden"
            id="file-upload"
            disabled={!selectedClient || !selectedDocType}
          />
          <Button
            className="bg-green-600 hover:bg-green-700"
            onClick={() => document.getElementById("file-upload")?.click()}
            disabled={!selectedClient || !selectedDocType}
          >
            Select Files
          </Button>
        </div>

        {/* Uploaded Documents List */}
        {uploadedDocuments.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              Recently Uploaded
              <Badge variant="secondary">{uploadedDocuments.length}</Badge>
            </h4>
            <div className="space-y-2">
              {uploadedDocuments.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-3 border rounded-lg bg-gray-50"
                >
                  <div className="flex items-center gap-3 flex-1">
                    {getStatusIcon(doc.status)}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm truncate">{doc.fileName}</p>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span>{doc.clientName}</span>
                        <span>•</span>
                        <span>{doc.documentType}</span>
                        <span>•</span>
                        <span>{formatFileSize(doc.fileSize)}</span>
                      </div>
                    </div>
                    <Badge
                      className={
                        doc.status === "verified"
                          ? "bg-green-100 text-green-800"
                          : doc.status === "processing"
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-blue-100 text-blue-800"
                      }
                    >
                      {doc.status}
                    </Badge>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleRemoveDocument(doc.id)}
                    className="ml-2"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-4 text-xs text-gray-500">
          <p>Supported document types: Passport, ID Card, Proof of Address, Bank Statements, Tax Documents</p>
        </div>
      </CardContent>
    </Card>
  );
}

