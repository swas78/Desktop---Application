Database Schema
Product: Automated Document Verification System (ADVS) Engine: SQLite with SQLCipher (single-user desktop). The same schema ports to PostgreSQL for LAN multi-user use (replace TEXT UUIDs with uuid, JSON text with jsonb). Migrations: Alembic. IDs: UUID stored as TEXT. Timestamps: ISO 8601 UTC text.
1. Entity Overview
users 1---* audit_log
vacancies 1---* applications 1---* documents 1---* document_pages
                              documents 1---* extraction_runs 1---* extracted_fields 1---* field_reviews
applications 1---* eligibility_results
processing_jobs 1---* job_items *---1 documents
review_items *---1 documents
settings, model_versions, reports, import_templates (standalone)
2. Tables
2.1 users
Column
Type
Constraints
Notes
id
TEXT
PK

username
TEXT
UNIQUE, NOT NULL

full_name
TEXT
NOT NULL

password_hash
TEXT
NOT NULL
bcrypt
role
TEXT
NOT NULL, CHECK in (admin, officer, reviewer)

is_active
INTEGER
NOT NULL DEFAULT 1

failed_logins
INTEGER
DEFAULT 0
Lockout at 5
locked_until
TEXT
NULL

created_at
TEXT
NOT NULL

last_login_at
TEXT
NULL

2.2 refresh_tokens
Column
Type
Constraints
id
TEXT
PK
user_id
TEXT
FK users(id), NOT NULL
token_hash
TEXT
NOT NULL
expires_at
TEXT
NOT NULL
revoked
INTEGER
DEFAULT 0
2.3 vacancies
Column
Type
Constraints
Notes
id
TEXT
PK

advt_no
TEXT
UNIQUE, NOT NULL

post_name
TEXT
NOT NULL

closing_date
TEXT
NOT NULL

rules_json
TEXT
NOT NULL
Eligibility rules (JSON)
status
TEXT
DEFAULT active
active or archived
created_by
TEXT
FK users(id)

created_at
TEXT
NOT NULL

updated_at
TEXT


2.4 applications
Column
Type
Constraints
Notes
id
TEXT
PK

registration_no
TEXT
UNIQUE, NOT NULL

vacancy_id
TEXT
FK vacancies(id), NOT NULL

full_name
TEXT
NOT NULL
Denormalized for search
father_name
TEXT


dob
TEXT

ISO date
category
TEXT

UR, OBC, SC, ST, EWS
is_pwd
INTEGER
DEFAULT 0

biodata_json
TEXT
NOT NULL
Full submitted biodata (encrypted at app level for sensitive keys)
status
TEXT
NOT NULL DEFAULT pending
pending, processing, verified, needs_review, rejected
eligibility
TEXT
DEFAULT unknown
eligible, not_eligible, needs_review, unknown
import_batch_id
TEXT
FK import_batches(id)

created_at
TEXT
NOT NULL

updated_at
TEXT


Indexes: (vacancy_id, status), (registration_no), (full_name).
2.5 import_batches and import_templates
Table
Columns
import_batches
id PK, filename, row_count, error_count, imported_by FK users, created_at
import_templates
id PK, name UNIQUE, mapping_json, created_by FK users, created_at
2.6 documents
Column
Type
Constraints
Notes
id
TEXT
PK

application_id
TEXT
FK applications(id), NOT NULL

original_filename
TEXT
NOT NULL

mime_type
TEXT
NOT NULL

file_path
TEXT
NOT NULL
Encrypted file in the store
file_sha256
TEXT
NOT NULL
Duplicate and tamper detection
size_bytes
INTEGER
NOT NULL

page_count
INTEGER
DEFAULT 1

declared_type
TEXT

Optional, from uploader
detected_type
TEXT

Classifier output
type_confidence
REAL


detected_language
TEXT


quality_score
REAL


status
TEXT
NOT NULL DEFAULT uploaded
uploaded, quality_failed, queued, processing, verified, mismatch, needs_review, rejected, failed
authenticity_risk
REAL

0 to 1
uploaded_by
TEXT
FK users(id)

uploaded_at
TEXT
NOT NULL

Indexes: (application_id), (status), (file_sha256).
2.7 document_pages
Column
Type
Constraints
id
TEXT
PK
document_id
TEXT
FK documents(id) ON DELETE CASCADE
page_no
INTEGER
NOT NULL
width
INTEGER

height
INTEGER

image_path
TEXT
Preprocessed render, encrypted
ocr_text
TEXT
Full text of the page
UNIQUE

(document_id, page_no)
2.8 extraction_runs
Column
Type
Constraints
Notes
id
TEXT
PK

document_id
TEXT
FK documents(id), NOT NULL

mode
TEXT
NOT NULL
quick or deep
model_version_id
TEXT
FK model_versions(id)
Reproducibility
started_at
TEXT
NOT NULL

total_ms
INTEGER

Overall time
timings_json
TEXT

Per-stage ms
status
TEXT

completed or failed
error_message
TEXT


is_latest
INTEGER
DEFAULT 1
Only one latest per document
2.9 extracted_fields
Column
Type
Constraints
Notes
id
TEXT
PK

run_id
TEXT
FK extraction_runs(id) ON DELETE CASCADE

document_id
TEXT
FK documents(id), NOT NULL

field_name
TEXT
NOT NULL
e.g. full_name, percentage
extracted_value
TEXT


normalized_value
TEXT

Standardized for comparison
expected_value
TEXT

From biodata
status
TEXT
NOT NULL
match, mismatch, low_confidence, not_found
confidence
REAL
NOT NULL
0 to 1
source
TEXT

qr, ocr, layout_model, rule
page_no
INTEGER


bbox_json
TEXT

x, y, w, h
reason
TEXT

Mismatch explanation
auto_accepted
INTEGER
DEFAULT 0
Counts toward the accuracy metric
Indexes: (document_id, field_name), (status), (run_id).
2.10 consistency_checks
Column
Type
Constraints
id
TEXT
PK
run_id
TEXT
FK extraction_runs(id) ON DELETE CASCADE
check_name
TEXT
NOT NULL
result
TEXT
NOT NULL (pass, fail, skipped)
detail
TEXT

2.11 review_items
Column
Type
Constraints
Notes
id
TEXT
PK

document_id
TEXT
FK documents(id), NOT NULL

reason
TEXT
NOT NULL
low_confidence, mismatch, unknown_type, handwriting, authenticity
priority
INTEGER
DEFAULT 0

status
TEXT
NOT NULL DEFAULT open
open, claimed, completed
assigned_to
TEXT
FK users(id)

created_at
TEXT
NOT NULL

completed_at
TEXT


2.12 field_reviews
Column
Type
Constraints
Notes
id
TEXT
PK

field_id
TEXT
FK extracted_fields(id), NOT NULL

review_item_id
TEXT
FK review_items(id)

reviewer_id
TEXT
FK users(id), NOT NULL

decision
TEXT
NOT NULL
accepted, corrected, rejected
corrected_value
TEXT


comment
TEXT


reviewed_at
TEXT
NOT NULL

used_for_training
INTEGER
DEFAULT 0

2.13 eligibility_results
Column
Type
Constraints
id
TEXT
PK
application_id
TEXT
FK applications(id), NOT NULL
vacancy_id
TEXT
FK vacancies(id), NOT NULL
verdict
TEXT
NOT NULL
reasons_json
TEXT
Per-rule outcomes
evaluated_at
TEXT
NOT NULL
is_latest
INTEGER
DEFAULT 1
2.14 processing_jobs and job_items
Table
Columns
processing_jobs
id PK, scope, vacancy_id FK, mode, state (queued, running, paused, completed, cancelled, failed), total, done, failed, avg_ms, created_by FK users, created_at, started_at, finished_at
job_items
id PK, job_id FK ON DELETE CASCADE, document_id FK, state (queued, running, done, failed), attempts, error_message, ms
Indexes: job_items(job_id, state).
2.15 model_versions
Column
Type
Notes
id
TEXT PK

name
TEXT
ocr, classifier, layout_extractor
version
TEXT
Semantic version
path
TEXT
Model file location
metrics_json
TEXT
Evaluation metrics at release
is_active
INTEGER
One active per name
installed_at
TEXT

2.16 settings
Column
Type
Notes
key
TEXT PK
e.g. confidence_threshold_default, manual_minutes_per_doc, enabled_languages
value_json
TEXT NOT NULL

updated_by
TEXT FK users

updated_at
TEXT

2.17 reports
Column
Type
Notes
id
TEXT PK

type
TEXT
verification, shortlist, audit
format
TEXT
pdf or xlsx
filters_json
TEXT

file_path
TEXT

created_by
TEXT FK users

created_at
TEXT

2.18 audit_log
Column
Type
Notes
id
INTEGER PK AUTOINCREMENT

ts
TEXT NOT NULL

user_id
TEXT FK users

action
TEXT NOT NULL
login, upload, edit_biodata, review_decision, export, and so on
entity_type
TEXT

entity_id
TEXT

details_json
TEXT
No raw PII values; field names and ids only
prev_hash
TEXT
Hash chain
hash
TEXT NOT NULL
SHA-256 of record plus prev_hash
Append-only: updates and deletes blocked by triggers.
3. SQL (core DDL excerpt)
PRAGMA foreign_keys = ON;

CREATE TABLE users (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin','officer','reviewer')),
  is_active INTEGER NOT NULL DEFAULT 1,
  failed_logins INTEGER DEFAULT 0,
  locked_until TEXT,
  created_at TEXT NOT NULL,
  last_login_at TEXT
);

CREATE TABLE vacancies (
  id TEXT PRIMARY KEY,
  advt_no TEXT UNIQUE NOT NULL,
  post_name TEXT NOT NULL,
  closing_date TEXT NOT NULL,
  rules_json TEXT NOT NULL,
  status TEXT DEFAULT 'active',
  created_by TEXT REFERENCES users(id),
  created_at TEXT NOT NULL,
  updated_at TEXT
);

CREATE TABLE applications (
  id TEXT PRIMARY KEY,
  registration_no TEXT UNIQUE NOT NULL,
  vacancy_id TEXT NOT NULL REFERENCES vacancies(id),
  full_name TEXT NOT NULL,
  father_name TEXT,
  dob TEXT,
  category TEXT,
  is_pwd INTEGER DEFAULT 0,
  biodata_json TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  eligibility TEXT DEFAULT 'unknown',
  import_batch_id TEXT REFERENCES import_batches(id),
  created_at TEXT NOT NULL,
  updated_at TEXT
);
CREATE INDEX idx_app_vacancy_status ON applications(vacancy_id, status);

CREATE TABLE documents (
  id TEXT PRIMARY KEY,
  application_id TEXT NOT NULL REFERENCES applications(id),
  original_filename TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_sha256 TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  page_count INTEGER DEFAULT 1,
  declared_type TEXT,
  detected_type TEXT,
  type_confidence REAL,
  detected_language TEXT,
  quality_score REAL,
  status TEXT NOT NULL DEFAULT 'uploaded',
  authenticity_risk REAL,
  uploaded_by TEXT REFERENCES users(id),
  uploaded_at TEXT NOT NULL
);
CREATE INDEX idx_doc_app ON documents(application_id);
CREATE INDEX idx_doc_status ON documents(status);

CREATE TABLE extraction_runs (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL REFERENCES documents(id),
  mode TEXT NOT NULL,
  model_version_id TEXT REFERENCES model_versions(id),
  started_at TEXT NOT NULL,
  total_ms INTEGER,
  timings_json TEXT,
  status TEXT,
  error_message TEXT,
  is_latest INTEGER DEFAULT 1
);

CREATE TABLE extracted_fields (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES extraction_runs(id) ON DELETE CASCADE,
  document_id TEXT NOT NULL REFERENCES documents(id),
  field_name TEXT NOT NULL,
  extracted_value TEXT,
  normalized_value TEXT,
  expected_value TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL,
  source TEXT,
  page_no INTEGER,
  bbox_json TEXT,
  reason TEXT,
  auto_accepted INTEGER DEFAULT 0
);
CREATE INDEX idx_field_doc ON extracted_fields(document_id, field_name);

CREATE TABLE field_reviews (
  id TEXT PRIMARY KEY,
  field_id TEXT NOT NULL REFERENCES extracted_fields(id),
  review_item_id TEXT REFERENCES review_items(id),
  reviewer_id TEXT NOT NULL REFERENCES users(id),
  decision TEXT NOT NULL CHECK (decision IN ('accepted','corrected','rejected')),
  corrected_value TEXT,
  comment TEXT,
  reviewed_at TEXT NOT NULL,
  used_for_training INTEGER DEFAULT 0
);

CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  user_id TEXT REFERENCES users(id),
  action TEXT NOT NULL,
  entity_type TEXT,
  entity_id TEXT,
  details_json TEXT,
  prev_hash TEXT,
  hash TEXT NOT NULL
);
CREATE TRIGGER audit_no_update BEFORE UPDATE ON audit_log
BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;
CREATE TRIGGER audit_no_delete BEFORE DELETE ON audit_log
BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;
(Remaining tables follow the column lists in section 2 with the same conventions.)
4. Key Queries for the Dashboard
-- Average and total processing time
SELECT COUNT(*) AS docs, AVG(total_ms) AS avg_ms
FROM extraction_runs WHERE is_latest = 1 AND status = 'completed';

-- Auto-verified rate
SELECT 1.0 * SUM(CASE WHEN status = 'verified' THEN 1 ELSE 0 END) / COUNT(*)
FROM documents WHERE status IN ('verified','mismatch','needs_review','rejected');

-- Mismatches by field
SELECT field_name, COUNT(*) AS n
FROM extracted_fields f JOIN extraction_runs r ON r.id = f.run_id AND r.is_latest = 1
WHERE f.status = 'mismatch' GROUP BY field_name ORDER BY n DESC;

-- Accuracy of auto-accepted fields (from reviewer audits and spot checks)
SELECT f.field_name,
       1.0 - AVG(CASE WHEN r.decision = 'corrected' THEN 1.0 ELSE 0 END) AS accuracy
FROM extracted_fields f JOIN field_reviews r ON r.field_id = f.id
WHERE f.auto_accepted = 1 GROUP BY f.field_name;
5. Data Protection Notes
• Database encrypted with SQLCipher; document files and page images encrypted with AES-256-GCM using a key held in the OS credential store or derived from the admin passphrase.
• Sensitive identifiers (for example, Aadhaar if ever present) are masked in stored text and logs.
• Retention setting: purge documents and extraction data after the configured period; keep the audit log.
• Backups: encrypted export of database plus file store, performed by an Admin.