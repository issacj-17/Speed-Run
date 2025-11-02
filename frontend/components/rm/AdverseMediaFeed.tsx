"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Rss } from "lucide-react";

export default function AdverseMediaFeed({ media }: { media: any[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Rss /> Adverse Media
        </CardTitle>
      </CardHeader>
      <CardContent>
        {media.length > 0 ? (
          <div className="space-y-4">
            {media.map((item, index) => (
              <div key={index}>
                <p className="font-semibold">{item.headline}</p>
                <p className="text-sm text-gray-500">{item.source} - {item.date}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No adverse media found.</p>
        )}
      </CardContent>
    </Card>
  );
}
