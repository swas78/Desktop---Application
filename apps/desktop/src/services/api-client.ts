// For: Single unified HTTP and WebSocket client wrapper for engine communication
// Must never: Make direct unauthenticated fetch requests or log sensitive tokens

const BASE_URL = "http://127.0.0.1:8000";

let inMemoryToken: string | null = localStorage.getItem("advs_token");

export function setAuthToken(token: string | null) {
  inMemoryToken = token;
  if (token) {
    localStorage.setItem("advs_token", token);
  } else {
    localStorage.removeItem("advs_token");
  }
}

export function getAuthToken(): string | null {
  return inMemoryToken;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (inMemoryToken) {
    headers.set("Authorization", `Bearer ${inMemoryToken}`);
  }
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    let errMsg = "An unexpected error occurred.";
    try {
      const errBody = await response.json();
      errMsg = errBody.detail?.message || errBody.error?.message || response.statusText;
    } catch {
      errMsg = `HTTP Error ${response.status}: ${response.statusText}`;
    }
    throw new Error(errMsg);
  }

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return response.json();
  }
  return response as unknown as T;
}

export const advsApi = {
  // Auth
  login: (data: { username: string; password: string }) =>
    request<{ access_token: string; user: { id: string; username: string; name: string; role: string } }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getMe: () => request<any>("/auth/me"),
  getHealth: () => request<any>("/health"),

  // Dashboard
  getDashboardSummary: () => request<any>("/dashboard/summary"),
  getDashboardMismatches: () => request<any[]>("/dashboard/mismatches"),
  getDashboardAccuracy: () => request<any[]>("/dashboard/accuracy"),
  getDashboardTimeseries: () => request<any[]>("/dashboard/timeseries"),

  // Vacancies
  getVacancies: () => request<any[]>("/vacancies"),
  createVacancy: (data: any) => request<any>("/vacancies", { method: "POST", body: JSON.stringify(data) }),

  // Applications
  getApplications: (params?: { vacancy_id?: string; status?: string; search?: string }) => {
    const q = new URLSearchParams();
    if (params?.vacancy_id) q.set("vacancy_id", params.vacancy_id);
    if (params?.status) q.set("status", params.status);
    if (params?.search) q.set("search", params.search);
    return request<any[]>(`/applications?${q.toString()}`);
  },
  getApplication: (id: string) => request<any>(`/applications/${id}`),
  createApplication: (data: any) => request<any>("/applications", { method: "POST", body: JSON.stringify(data) }),
  importApplications: (data: { rows: any[]; vacancy_id?: string }) =>
    request<{ status: string; imported: number }>("/applications/import", { method: "POST", body: JSON.stringify(data) }),
  exportApplicationAlerts: (appId: string) =>
    request<{ registration_no: string; alerts: Array<{ field: string; message: string }> }>(`/applications/${appId}/alerts/export`, { method: "POST" }),

  // Verification & Instant Check
  instantCheck: (formData: FormData) =>
    request<any>("/verify/instant", { method: "POST", body: formData }),
  verifyPreset: (sampleType: string) =>
    request<any>(`/verify/preset/${sampleType}`, { method: "POST" }),
  uploadDocument: (appId: string, formData: FormData) =>
    request<any>(`/applications/${appId}/documents`, { method: "POST", body: formData }),
  getDocumentFileUrl: (docId: string) => `${BASE_URL}/documents/${docId}/file`,

  // Review Queue & Workbench
  getReviewQueue: (status?: string) => request<any[]>(`/review/queue?status=${status || "open"}`),
  claimReviewItem: (itemId: string) => request<any>(`/review/queue/${itemId}/claim`, { method: "POST" }),
  getReviewItemDetail: (itemId: string) => request<any>(`/review/items/${itemId}/detail`),
  submitFieldReview: (fieldId: string, data: { decision: string; corrected_value?: string; comment?: string }) =>
    request<any>(`/fields/${fieldId}`, { method: "PATCH", body: JSON.stringify(data) }),
  completeReviewItem: (itemId: string) => request<any>(`/review/queue/${itemId}/complete`, { method: "POST" }),

  // Jobs
  getJobs: () => request<any[]>("/jobs"),
  createJob: (data: { scope: string; vacancy_id?: string; mode?: string }) =>
    request<any>("/jobs", { method: "POST", body: JSON.stringify(data) }),
  pauseJob: (jobId: string) => request<any>(`/jobs/${jobId}/pause`, { method: "POST" }),
  resumeJob: (jobId: string) => request<any>(`/jobs/${jobId}/resume`, { method: "POST" }),
  cancelJob: (jobId: string) => request<any>(`/jobs/${jobId}/cancel`, { method: "POST" }),

  // Eligibility
  evaluateApplicationEligibility: (appId: string) =>
    request<any>(`/applications/${appId}/eligibility/evaluate`, { method: "POST" }),
  evaluateVacancyBatch: (vacId: string) =>
    request<any>(`/vacancies/${vacId}/eligibility/run`, { method: "POST" }),

  // Reports
  createReport: (data: { type: string; format: string; vacancy_id?: string }) =>
    request<any>("/reports", { method: "POST", body: JSON.stringify(data) }),
  getReportDownloadUrl: (reportId: string) => `${BASE_URL}/reports/${reportId}/download`,

  // Settings & Admin
  getSettings: () => request<Record<string, any>>("/settings"),
  updateSettings: (data: Record<string, any>) => request<any>("/settings", { method: "PUT", body: JSON.stringify(data) }),
  getUsers: () => request<any[]>("/users"),
  createUser: (data: any) => request<any>("/users", { method: "POST", body: JSON.stringify(data) }),
  getAuditTrail: () => request<{ chain_valid: boolean; entries: any[] }>("/audit"),
  getModels: () => request<any[]>("/models"),
};
