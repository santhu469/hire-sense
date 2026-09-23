// Mirrors backend/app/schemas/*.py and the enums in backend/app/models/*.py.

export type UserRole = "admin" | "recruiter" | "viewer";

export interface User {
  id: string;
  email: string;
  role: UserRole;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type JobDescriptionStatus = "draft" | "active" | "closed";

export interface EvaluationCriteriaItem {
  category: string;
  weight: number;
  version: number;
}

export interface JobDescription {
  id: string;
  title: string;
  raw_text: string;
  structured_requirements: Record<string, unknown>;
  status: JobDescriptionStatus;
  created_by: string;
  created_at: string;
  criteria: EvaluationCriteriaItem[];
}

export type DecisionStatus = "shortlisted" | "hold" | "rejected";

export type ProcessingStatus =
  | "pending"
  | "parsing"
  | "evaluating"
  | "completed"
  | "failed";

export interface EvaluationInsights {
  summary: string;
  strengths: string[];
  matching_skills: string[];
  gaps: string[];
  differentiators: string[];
  concerns: string[];
  recommendation: string;
}

export interface Evaluation {
  id: string;
  candidate_id: string;
  jd_id: string;
  criteria_version: number;
  overall_score: number;
  category_scores: Record<string, number>;
  insights: EvaluationInsights;
  is_latest: boolean;
  created_at: string;
}

export interface CandidateProfile {
  name: string | null;
  email: string | null;
  phone: string | null;
  skills: string[];
  experience_years: number | null;
  experience_timeline: string[];
  education: string[];
  certifications: string[];
}

export interface CandidateUploadResult {
  id: string;
  jd_id: string;
  processing_status: ProcessingStatus;
  uploaded_at: string;
}

export interface Candidate {
  id: string;
  jd_id: string;
  current_status: DecisionStatus | null;
  processing_status: ProcessingStatus;
  error_message: string | null;
  parsed_profile: CandidateProfile | null;
  uploaded_at: string;
  latest_evaluation: Evaluation | null;
}

// The pipeline states where a background job is still working; the ranked
// list polls while any candidate is in one of these.
export const IN_PROGRESS_STATUSES: ProcessingStatus[] = [
  "pending",
  "parsing",
  "evaluating",
];
