"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { CandidateRankingTable } from "@/components/candidates/candidate-ranking-table";
import { CandidateUpload } from "@/components/candidates/candidate-upload";
import * as api from "@/lib/api";
import { IN_PROGRESS_STATUSES } from "@/lib/types";

export default function JobDescriptionDetailPage() {
  const { jdId } = useParams<{ jdId: string }>();

  const { data: jd, isLoading: jdLoading } = useQuery({
    queryKey: ["job-description", jdId],
    queryFn: () => api.getJobDescription(jdId),
  });

  const { data: candidates, isLoading: candidatesLoading } = useQuery({
    queryKey: ["candidates", jdId],
    queryFn: () => api.listRankedCandidates(jdId),
    refetchInterval: (query) => {
      const rows = query.state.data;
      const stillProcessing = rows?.some((c) => IN_PROGRESS_STATUSES.includes(c.processing_status));
      return stillProcessing ? 3_000 : false;
    },
  });

  if (jdLoading) return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (!jd) return <p className="text-sm text-destructive">Job description not found.</p>;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-semibold">{jd.title}</h1>
          <Badge variant="outline">{jd.status}</Badge>
        </div>
        <p className="mt-2 whitespace-pre-wrap text-sm text-muted-foreground">{jd.raw_text}</p>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {jd.criteria.map((c) => (
            <Badge key={c.category} variant="secondary" className="text-xs">
              {c.category} — {c.weight}%
            </Badge>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-3 rounded-lg border p-4">
        <h2 className="text-sm font-medium">Upload a resume</h2>
        <CandidateUpload jdId={jdId} />
      </div>

      <div>
        <h2 className="mb-3 text-lg font-semibold">Candidates</h2>
        {candidatesLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
        {candidates && candidates.length === 0 && (
          <p className="text-sm text-muted-foreground">No candidates uploaded yet.</p>
        )}
        {candidates && candidates.length > 0 && <CandidateRankingTable candidates={candidates} />}
      </div>
    </div>
  );
}
