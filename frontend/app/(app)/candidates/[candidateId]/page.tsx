"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";

import { StatusChangeDialog } from "@/components/candidates/status-change-dialog";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import * as api from "@/lib/api";
import { IN_PROGRESS_STATUSES } from "@/lib/types";

const INSIGHT_SECTIONS: { key: "strengths" | "matching_skills" | "gaps" | "differentiators" | "concerns"; label: string }[] = [
  { key: "strengths", label: "Strengths" },
  { key: "matching_skills", label: "Matching skills" },
  { key: "gaps", label: "Gaps" },
  { key: "differentiators", label: "Differentiators" },
  { key: "concerns", label: "Concerns" },
];

export default function CandidateDetailPage() {
  const { candidateId } = useParams<{ candidateId: string }>();

  const { data: candidate, isLoading } = useQuery({
    queryKey: ["candidate", candidateId],
    queryFn: () => api.getCandidate(candidateId),
    refetchInterval: (query) =>
      query.state.data && IN_PROGRESS_STATUSES.includes(query.state.data.processing_status) ? 3_000 : false,
  });

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (!candidate) return <p className="text-sm text-destructive">Candidate not found.</p>;

  const evaluation = candidate.latest_evaluation;
  const profile = candidate.parsed_profile;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{profile?.name ?? "Candidate"}</h1>
          <Link
            href={`/job-descriptions/${candidate.jd_id}`}
            className="text-sm text-muted-foreground underline underline-offset-4"
          >
            Back to job description
          </Link>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline">{candidate.processing_status}</Badge>
          {candidate.current_status && <Badge>{candidate.current_status}</Badge>}
          <StatusChangeDialog candidateId={candidate.id} jdId={candidate.jd_id} />
        </div>
      </div>

      {candidate.processing_status === "failed" && (
        <p className="rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive">
          Evaluation failed: {candidate.error_message}
        </p>
      )}
      {IN_PROGRESS_STATUSES.includes(candidate.processing_status) && (
        <p className="text-sm text-muted-foreground">Evaluation in progress…</p>
      )}

      {profile && (
        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2 text-sm">
            <p>{profile.email}</p>
            <p>{profile.phone}</p>
            <p>{profile.experience_years != null ? `${profile.experience_years} years experience` : null}</p>
            <div className="flex flex-wrap gap-1.5">
              {profile.skills.map((skill) => (
                <Badge key={skill} variant="secondary">
                  {skill}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {evaluation && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Evaluation</span>
                <span className="text-2xl font-semibold">{evaluation.overall_score.toFixed(1)}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(evaluation.category_scores).map(([category, score]) => (
                  <Badge key={category} variant="outline">
                    {category}: {score.toFixed(0)}
                  </Badge>
                ))}
              </div>
              <p className="text-sm">{evaluation.insights.summary}</p>
              <p className="text-sm font-medium">Recommendation: {evaluation.insights.recommendation}</p>
            </CardContent>
          </Card>

          <div className="grid gap-4 sm:grid-cols-2">
            {INSIGHT_SECTIONS.map(({ key, label }) => {
              const items = evaluation.insights[key];
              if (!items || items.length === 0) return null;
              return (
                <Card key={key}>
                  <CardHeader>
                    <CardTitle className="text-sm">{label}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="list-disc space-y-1 pl-4 text-sm text-muted-foreground">
                      {items.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
