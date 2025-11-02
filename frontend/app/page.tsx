"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Shield, Users, FileText } from "lucide-react";

export default function RoleSelectorPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 flex items-center justify-center p-6">
      <div className="max-w-4xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Image
              src="/images/julius-baer-group-logo.png"
              alt="Julius Baer Group Logo"
              width={64}
              height={64}
            />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Julius Baer
          </h1>
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">
            KYC Document Verification Platform
          </h2>
          <p className="text-gray-600">
            Select your role to continue
          </p>
        </div>

        {/* Role Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Compliance Officer Card */}
          <Card className="hover:shadow-xl transition-shadow cursor-pointer border-2 hover:border-blue-500">
            <CardHeader>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-blue-600" />
              </div>
              <CardTitle className="text-2xl">Compliance Officer</CardTitle>
              <CardDescription className="text-base">
                Review KYC documents, assess risk scores, and manage compliance workflows
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 mb-6 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                  Review red flags and critical alerts
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                  Assess risk scores and breakdowns
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                  Verify source of wealth
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                  Approve or reject KYC applications
                </li>
              </ul>
              <Button
                className="w-full bg-blue-600 hover:bg-blue-700"
                size="lg"
                onClick={() => router.push("/compliance")}
              >
                Enter Compliance Dashboard
              </Button>
            </CardContent>
          </Card>

          {/* Relationship Manager Card */}
          <Card className="hover:shadow-xl transition-shadow cursor-pointer border-2 hover:border-green-500">
            <CardHeader>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-green-600" />
              </div>
              <CardTitle className="text-2xl">Relationship Manager</CardTitle>
              <CardDescription className="text-base">
                Manage client profiles, upload documents, and monitor alerts
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 mb-6 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-green-600 rounded-full"></span>
                  View client demographic profiles
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-green-600 rounded-full"></span>
                  Upload client documents (PDF, JPG, PNG)
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-green-600 rounded-full"></span>
                  Monitor fraud alerts for clients
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-green-600 rounded-full"></span>
                  Track risk scorecards
                </li>
              </ul>
              <Button
                className="w-full bg-green-600 hover:bg-green-700"
                size="lg"
                onClick={() => router.push("/rm")}
              >
                Enter RM Dashboard
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Footer Note */}
        <div className="mt-8 text-center">
          <Card className="bg-gray-50 border-gray-200">
            <CardContent className="pt-6">
              <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
                <FileText className="h-4 w-4" />
                <span>
                  This platform focuses on document verification, risk assessment, and compliance workflows
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
