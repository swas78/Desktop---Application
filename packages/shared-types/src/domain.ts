// For: Domain entity types and status enums for ADVS verification records
// Must never: Contain API route logic, UI rendering, or database drivers

export type UserRole = "admin" | "officer" | "reviewer";

export interface User {
  id: string;
  username: string;
  fullName: string;
  role: UserRole;
  isActive: boolean;
  failedLogins: number;
  lockedUntil: string | null;
  createdAt: string;
  lastLoginAt: string | null;
}

export interface VacancyRules {
  minQualification: string;
  allowedBranches: string[];
  minPercentage: number;
  gateRequired: boolean;
  gateValidityYears: number;
  maxAge: {
    UR: number;
    OBC: number;
    SC: number;
    ST: number;
    PwD_extra: number;
  };
  requiredDocuments: string[];
}

export interface Vacancy {
  id: string;
  advtNo: string;
  postName: string;
  closingDate: string;
  rules: VacancyRules;
  status: "active" | "archived";
  createdBy: string;
  createdAt: string;
  updatedAt: string | null;
}

export interface QualificationInfo {
  degree: string;
  branch: string;
  university: string;
  year: number;
  percentage: number;
}

export interface GateInfo {
  regNo: string;
  year: number;
  score: number;
  air?: number;
  marks?: number;
}

export interface ExperienceInfo {
  org: string;
  designation: string;
  from: string;
  to: string;
}

export interface Biodata {
  fullName: string;
  fatherName?: string;
  dob?: string;
  category?: "UR" | "OBC" | "SC" | "ST" | "EWS";
  pwd?: boolean;
  qualification?: QualificationInfo;
  gate?: GateInfo;
  experience?: ExperienceInfo[];
  [key: string]: unknown;
}

export type ApplicationStatus =
  | "pending"
  | "processing"
  | "verified"
  | "needs_review"
  | "rejected";

export type EligibilityVerdict =
  | "eligible"
  | "not_eligible"
  | "needs_review"
  | "unknown";

export interface Application {
  id: string;
  registrationNo: string;
  vacancyId: string;
  fullName: string;
  fatherName: string | null;
  dob: string | null;
  category: string | null;
  isPwd: boolean;
  biodata: Biodata;
  status: ApplicationStatus;
  eligibility: EligibilityVerdict;
  importBatchId: string | null;
  createdAt: string;
  updatedAt: string | null;
}

export type DocumentStatus =
  | "uploaded"
  | "quality_failed"
  | "queued"
  | "processing"
  | "verified"
  | "mismatch"
  | "needs_review"
  | "rejected"
  | "failed";

export interface DocumentRecord {
  id: string;
  applicationId: string;
  originalFilename: string;
  mimeType: string;
  filePath: string;
  fileSha256: string;
  sizeBytes: number;
  pageCount: number;
  declaredType: string | null;
  detectedType: string | null;
  typeConfidence: number | null;
  detectedLanguage: string | null;
  qualityScore: number | null;
  status: DocumentStatus;
  authenticityRisk: number | null;
  uploadedBy: string | null;
  uploadedAt: string;
}

export interface BBox {
  page: number;
  x: number;
  y: number;
  w: number;
  h: number;
}

export type FieldStatus = "match" | "mismatch" | "low_confidence" | "not_found";

export interface ExtractedField {
  id?: string;
  name: string;
  extracted: string | null;
  normalized?: string | null;
  expected?: string | null;
  status: FieldStatus;
  confidence: number;
  source: "qr" | "ocr" | "layout_model" | "rule";
  pageNo?: number;
  bbox?: BBox | null;
  reason?: string | null;
  autoAccepted?: boolean;
}

export interface ReviewItem {
  id: string;
  documentId: string;
  reason: "low_confidence" | "mismatch" | "unknown_type" | "handwriting" | "authenticity";
  priority: number;
  status: "open" | "claimed" | "completed";
  assignedTo: string | null;
  createdAt: string;
  completedAt: string | null;
}

export type ReviewDecision = "accepted" | "corrected" | "rejected";

export interface FieldReview {
  id: string;
  fieldId: string;
  reviewItemId?: string;
  reviewerId: string;
  decision: ReviewDecision;
  correctedValue?: string;
  comment?: string;
  reviewedAt: string;
  usedForTraining?: boolean;
}
