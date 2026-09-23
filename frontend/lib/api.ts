import { clearTokens, getStoredTokens, storeTokens } from "@/lib/auth-storage";
import type {
  Candidate,
  CandidateUploadResult,
  DecisionStatus,
  JobDescription,
  TokenResponse,
  User,
} from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function parseErrorDetail(response: Response): Promise<string> {
  try {
    const body = await response.json();
    return body.detail ?? response.statusText;
  } catch {
    return response.statusText;
  }
}

async function rawFetch(path: string, init: RequestInit): Promise<Response> {
  return fetch(`${API_BASE_URL}${path}`, init);
}

let refreshInFlight: Promise<string | null> | null = null;

// Refreshes the access token exactly once even if several requests 401 at
// the same time -- concurrent callers share the same in-flight promise.
async function refreshAccessTokenOnce(): Promise<string | null> {
  if (refreshInFlight) return refreshInFlight;

  refreshInFlight = (async () => {
    const tokens = getStoredTokens();
    if (!tokens) return null;

    const response = await rawFetch("/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: tokens.refreshToken }),
    });
    if (!response.ok) return null;

    const data: TokenResponse = await response.json();
    storeTokens(data.access_token, data.refresh_token);
    return data.access_token;
  })();

  try {
    return await refreshInFlight;
  } finally {
    refreshInFlight = null;
  }
}

interface ApiFetchOptions extends RequestInit {
  auth?: boolean; // default true
}

async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { auth = true, headers, ...rest } = options;

  const buildHeaders = (): HeadersInit => {
    const merged: Record<string, string> = { ...(headers as Record<string, string>) };
    if (auth) {
      const tokens = getStoredTokens();
      if (tokens) merged.Authorization = `Bearer ${tokens.accessToken}`;
    }
    return merged;
  };

  let response = await rawFetch(path, { ...rest, headers: buildHeaders() });

  if (response.status === 401 && auth) {
    const newAccessToken = await refreshAccessTokenOnce();
    if (!newAccessToken) {
      clearTokens();
      // A full reload, not router.push -- this is a plain module with no
      // access to the Next.js router, and a hard reset is appropriate here
      // anyway: it clears all in-memory app/query state tied to the now-dead session.
      // eslint-disable-next-line @next/next/no-location-assign-relative-destination
      if (typeof window !== "undefined") window.location.href = "/login";
      throw new ApiError(401, "Session expired");
    }
    response = await rawFetch(path, { ...rest, headers: buildHeaders() });
  }

  if (!response.ok) {
    throw new ApiError(response.status, await parseErrorDetail(response));
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

function jsonInit(method: string, body: unknown): RequestInit {
  return { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
}

export async function register(email: string, password: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/auth/register", { auth: false, ...jsonInit("POST", { email, password }) });
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/auth/login", { auth: false, ...jsonInit("POST", { email, password }) });
}

export async function me(): Promise<User> {
  return apiFetch<User>("/auth/me");
}

export async function createJobDescription(title: string, rawText: string): Promise<JobDescription> {
  return apiFetch<JobDescription>("/job-descriptions", jsonInit("POST", { title, raw_text: rawText }));
}

export async function listJobDescriptions(): Promise<JobDescription[]> {
  return apiFetch<JobDescription[]>("/job-descriptions");
}

export async function getJobDescription(jdId: string): Promise<JobDescription> {
  return apiFetch<JobDescription>(`/job-descriptions/${jdId}`);
}

export async function uploadCandidate(jdId: string, file: File): Promise<CandidateUploadResult> {
  const formData = new FormData();
  formData.append("file", file);
  return apiFetch<CandidateUploadResult>(`/job-descriptions/${jdId}/candidates`, {
    method: "POST",
    body: formData,
  });
}

export async function listRankedCandidates(
  jdId: string,
  params?: { statusFilter?: DecisionStatus; minScore?: number },
): Promise<Candidate[]> {
  const query = new URLSearchParams();
  if (params?.statusFilter) query.set("status_filter", params.statusFilter);
  if (params?.minScore !== undefined) query.set("min_score", String(params.minScore));
  const qs = query.toString();
  return apiFetch<Candidate[]>(`/job-descriptions/${jdId}/candidates${qs ? `?${qs}` : ""}`);
}

export async function getCandidate(candidateId: string): Promise<Candidate> {
  return apiFetch<Candidate>(`/candidates/${candidateId}`);
}

export async function changeCandidateStatus(
  candidateId: string,
  status: DecisionStatus,
  reasonNote: string | null,
): Promise<Candidate> {
  return apiFetch<Candidate>(
    `/candidates/${candidateId}/status`,
    { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status, reason_note: reasonNote }) },
  );
}
