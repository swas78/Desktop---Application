// For: API request and response data contracts between desktop app and engine
// Must never: Store local credentials or execute HTTP operations directly

import {
  User,
  UserRole,
  ExtractedField,
  DocumentRecord,
  ReviewDecision,
  Application,
  Biodata,
} from "./domain";

export interface LoginPayload {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: {
    id: string;
    username: string;
    name: string;
    role: UserRole;
  };
}

export interface ConsistencyCheck {
  name: string;
  result: "pass" | "fail" | "skipped";
  detail?: string;
}

export interface AuthenticityReport {
  risk_score: number;
  flags: string[];
}

export interface InstantCheckResult {
  document_type: string;
  type_confidence: number;
  processing_ms: number;
  model_version: string;
  quality_score: number;
  fields: ExtractedField[];
  checks: ConsistencyCheck[];
  authenticity: AuthenticityReport;
  alerts: string[];
}

export interface JobProgressEvent {
  type: "document_done" | "job_state_changed" | "job_error";
  job_id: string;
  document_id?: string;
  status?: string;
  ms?: number;
  done: number;
  total: number;
  state?: "queued" | "running" | "paused" | "completed" | "cancelled" | "failed";
}

export interface ProcessingJob {
  id: string;
  scope: string;
  vacancyId: string | null;
  mode: "quick" | "deep";
  state: "queued" | "running" | "paused" | "completed" | "cancelled" | "failed";
  total: number;
  done: number;
  failed: number;
  avgMs: number;
  createdBy: string | null;
  createdAt: string;
  startedAt: string | null;
  finishedAt: string | null;
}

export interface RuleOutcome {
  rule: string;
  required: unknown;
  actual: unknown;
  passed: boolean;
  message?: string;
}

export interface EligibilityResult {
  verdict: "eligible" | "not_eligible" | "needs_review";
  reasons: RuleOutcome[];
}

export interface DashboardSummary {
  processed: number;
  avg_ms: number;
  p95_ms: number;
  auto_verified_percent: number;
  review_percent: number;
  hours_saved: number;
  manual_minutes_per_doc: number;
  ledger: Array<{
    document_type: string;
    processed: number;
    auto_verified: number;
    sent_to_review: number;
    mismatches: number;
    avg_ms: number;
  }>;
}

export interface MismatchStat {
  field_name: string;
  reason: string;
  count: number;
}

export interface AccuracyStat {
  field_name: string;
  document_type: string;
  accuracy: number;
  sample_size: number;
  review_rate: number;
}

export interface AppSettings {
  confidence_threshold_default: number;
  manual_minutes_per_doc: number;
  enabled_languages: string[];
  auto_accept_threshold: number;
  date_tolerance_days: number;
  percentage_tolerance: number;
}

export interface AuditLogEntry {
  id: number;
  ts: string;
  user_id: string | null;
  action: string;
  entity_type: string | null;
  entity_id: string | null;
  details_json: string;
  prev_hash: string | null;
  hash: string;
}

export interface ReviewQueueItemDetail {
  id: string;
  document: DocumentRecord;
  application: Application;
  fields: ExtractedField[];
  reason: string;
  priority: number;
  status: "open" | "claimed" | "completed";
  assignedTo: string | null;
  createdAt: string;
}

export interface FieldReviewDecisionPayload {
  decision: ReviewDecision;
  corrected_value?: string;
  comment?: string;
}

export interface MismatchAlertExport {
  registration_no: string;
  alerts: Array<{
    field: string;
    message: string;
  }>;
}
