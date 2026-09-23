"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import * as api from "@/lib/api";

export default function JobDescriptionsPage() {
  const { data: jds, isLoading, error } = useQuery({
    queryKey: ["job-descriptions"],
    queryFn: api.listJobDescriptions,
  });

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Job Descriptions</h1>
        <Button render={<Link href="/job-descriptions/new" />}>New job description</Button>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
      {error && <p className="text-sm text-destructive">Failed to load job descriptions.</p>}

      {jds && jds.length === 0 && (
        <p className="text-sm text-muted-foreground">
          No job descriptions yet.{" "}
          <Link href="/job-descriptions/new" className="text-primary underline underline-offset-4">
            Create one
          </Link>
          .
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {jds?.map((jd) => (
          <Link key={jd.id} href={`/job-descriptions/${jd.id}`}>
            <Card className="h-full transition-colors hover:bg-muted/50">
              <CardHeader>
                <CardTitle className="flex items-center justify-between gap-2">
                  <span>{jd.title}</span>
                  <Badge variant="outline">{jd.status}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="line-clamp-3 text-sm text-muted-foreground">{jd.raw_text}</p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {jd.criteria.map((c) => (
                    <Badge key={c.category} variant="secondary" className="text-xs">
                      {c.category} {c.weight}%
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
