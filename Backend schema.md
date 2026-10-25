 Backend Schema (API Specification)
Product: Automated Document Verification System (ADVS) Service: Python engine (FastAPI), served on 127.0.0.1:<random-port> Base path: /api/v1 | Format: JSON | Auth: Authorization: Bearer <JWT>
1. Conventions
• Timestamps are ISO 8601 UTC. IDs are UUIDs (strings).
• Pagination: ?page=1&page_size=50; response includes total.
• Errors use one shape:
{ "error": { "code": "VALIDATION_ERROR", "message": "Human readable", "details": [ { "field": "dob", "issue": "invalid format" } ] } }
HTTP
Code
Meaning
400
VALIDATION_ERROR
Bad input
401
UNAUTHENTICATED
Missing or expired token
403
FORBIDDEN
Role not allowed
404
NOT_FOUND
Missing resource
409
CONFLICT
Duplicate or state conflict
413
FILE_TOO_LARGE
Over upload limit
422
UNREADABLE_DOCUMENT
Failed quality gate
500
INTERNAL_ERROR
Unexpected failure
2. Roles and Permissions
Endpoint group
Admin
Officer
Reviewer
Auth
yes
yes
yes
Users
yes
no
no
Vacancies and rules
yes
read
read
Applications and documents
yes
yes
read
Processing jobs
yes
yes
no
Review
yes
yes
yes
Dashboard and reports
yes
yes
read
Settings and audit
yes
no
no
3. Authentication
Method
Path
Description
POST
/auth/login
Username and password, returns access and refresh tokens
POST
/auth/refresh
New access token
POST
/auth/logout
Revoke refresh token
GET
/auth/me
Current user and role
// POST /auth/login request
{ "username": "officer1", "password": "********" }
// response
{ "access_token": "jwt", "refresh_token": "jwt", "expires_in": 900, "user": { "id": "uuid", "name": "A. Kumar", "role": "officer" } }
4. Users (Admin)
Method
Path
Description
GET
/users
List users
POST
/users
Create user (username, full_name, role, password)
PATCH
/users/{id}
Update role, active flag, reset password
DELETE
/users/{id}
Deactivate
5. Vacancies and Eligibility Rules
Method
Path
Description
GET
/vacancies
List vacancies
POST
/vacancies
Create vacancy with rules
GET
/vacancies/{id}
Detail
PUT
/vacancies/{id}
Replace
DELETE
/vacancies/{id}
Archive
{
  "advt_no": "RAC/2024/01",
  "post_name": "Scientist B (Electronics)",
  "closing_date": "2024-12-31",
  "rules": {
    "min_qualification": "BE/BTech",
    "allowed_branches": ["ECE", "EEE"],
    "min_percentage": 60,
    "gate_required": true,
    "gate_validity_years": 3,
    "max_age": { "UR": 28, "OBC": 31, "SC": 33, "ST": 33, "PwD_extra": 10 },
    "required_documents": ["degree_marksheet", "gate_scorecard"]
  }
}
6. Applications and Biodata
Method
Path
Description
POST
/applications/import
Upload CSV/Excel/JSON with a column mapping; returns import job
GET
/applications
List with filters: vacancy_id, status, search
POST
/applications
Create single application
GET
/applications/{id}
Application with documents and summary
PATCH
/applications/{id}
Edit biodata (audited)
// Application object
{
  "id": "uuid",
  "registration_no": "RAC24000123",
  "vacancy_id": "uuid",
  "biodata": {
    "full_name": "Rahul Kumar Sharma", "father_name": "Mohan Sharma",
    "dob": "1999-05-14", "category": "OBC", "pwd": false,
    "qualification": { "degree": "BTech", "branch": "ECE", "university": "XYZ University", "year": 2021, "percentage": 74.2 },
    "gate": { "reg_no": "EC21S12345", "year": 2023, "score": 612 },
    "experience": [ { "org": "ABC Ltd", "designation": "Engineer", "from": "2021-07-01", "to": "2023-06-30" } ]
  },
  "status": "pending | processing | verified | needs_review | rejected",
  "eligibility": "eligible | not_eligible | needs_review | unknown"
}
7. Documents
Method
Path
Description
POST
/applications/{id}/documents
Multipart upload (file, optional declared_type)
POST
/documents/bulk-link
Link a folder of files to applications by naming rule
GET
/documents/{id}
Metadata and status
GET
/documents/{id}/file
Decrypted original (streamed)
GET
/documents/{id}/pages/{n}/image
Page render for the viewer
DELETE
/documents/{id}
Remove (audited)
8. Processing
8.1 Instant check (single document)
POST /verify/instant (multipart: file, biodata JSON, optional declared_type). Synchronous, returns in 3 seconds or less.
{
  "document_type": "degree_marksheet", "type_confidence": 0.99,
  "processing_ms": 2140, "model_version": "1.3.0",
  "fields": [
    { "name": "full_name", "extracted": "RAHUL K SHARMA", "expected": "Rahul Kumar Sharma",
      "status": "match", "confidence": 0.98, "source": "ocr+qr",
      "bbox": { "page": 1, "x": 120, "y": 340, "w": 410, "h": 36 } },
    { "name": "percentage", "extracted": "72.4", "expected": "74.2",
      "status": "mismatch", "confidence": 0.96, "reason": "Value differs by 1.8" }
  ],
  "checks": [ { "name": "marks_total_consistent", "result": "pass" } ],
  "authenticity": { "risk_score": 0.08, "flags": [] },
  "alerts": [ "Percentage in form (74.2) does not match document (72.4)" ]
}
8.2 Batch jobs
Method
Path
Description
POST
/jobs
Create job: `{ "scope": "vacancy
GET
/jobs
List jobs
GET
/jobs/{id}
Progress: total, done, failed, avg_ms, state
POST
/jobs/{id}/pause
Pause
POST
/jobs/{id}/resume
Resume
POST
/jobs/{id}/cancel
Cancel
POST
/documents/{id}/reprocess
Re-run with mode=deep
WS
/ws/jobs/{id}
Live progress events
// WebSocket event
{ "type": "document_done", "job_id": "uuid", "document_id": "uuid", "status": "needs_review", "ms": 2310, "done": 412, "total": 5000 }
9. Verification Results and Review
Method
Path
Description
GET
/applications/{id}/verification
Latest result per document and field
GET
/review/queue
Items needing review: filters doc_type, reason, assigned_to
POST
/review/queue/{item_id}/claim
Assign to current reviewer
PATCH
/fields/{field_id}
Reviewer decision
POST
/review/queue/{item_id}/complete
Close item and recompute application status
// PATCH /fields/{field_id}
{ "decision": "accepted | corrected | rejected", "corrected_value": "72.4", "comment": "Seen on page 2" }
10. Eligibility
Method
Path
Description
POST
/applications/{id}/eligibility/evaluate
Run rules; returns verdict and per-rule reasons
POST
/vacancies/{id}/eligibility/run
Evaluate all applications for a vacancy
{ "verdict": "not_eligible", "reasons": [ { "rule": "min_percentage", "required": 60, "actual": 55.8, "passed": false } ] }
11. Dashboard and Reports
Method
Path
Description
GET
/dashboard/summary
KPI cards: processed, avg ms, p95 ms, auto-verified %, review %, hours saved
GET
/dashboard/timeseries
Metric over time (metric, from, to, interval)
GET
/dashboard/mismatches
Counts by field and reason
GET
/dashboard/accuracy
Accuracy per field and document type from reviewer feedback
POST
/reports
Generate report `{ "type": "verification
GET
/reports/{id}/download
File download
Hours saved estimate: documents_auto_verified x manual_minutes_per_doc / 60, where manual_minutes_per_doc is a setting (default 4).
12. Settings, Models, Audit
Method
Path
Description
GET / PUT
/settings
Confidence thresholds, languages, accuracy tolerances, manual minutes per doc
GET
/models
Installed models and versions
POST
/models/activate
Activate a model version
GET
/audit
Audit log with filters
GET
/health
Engine health, model load state, queue depth
POST
/training/export
Export reviewer corrections as a labelled dataset
13. Notification Output
Optional mismatch alert export for applicants (sent via the portal or by email by RAC, since ADVS is offline).
POST /applications/{id}/alerts/export returns:
{ "registration_no": "RAC24000123", "alerts": [ { "field": "percentage", "message": "Entered 74.2 but document shows 72.4. Please correct your application." } ] }
14. Internal Engine Interfaces (for developers)
class Stage(Protocol):
    name: str
    def run(self, ctx: PipelineContext) -> PipelineContext: ...

# Pipeline order
[Ingest, Preprocess, Classify, QRDecode, OCR, Translate, Extract, Verify, Authenticity]

class ExtractedField(BaseModel):
    name: str
    value: str | None
    confidence: float
    source: Literal["qr", "ocr", "layout_model", "rule"]
    bbox: BBox | None