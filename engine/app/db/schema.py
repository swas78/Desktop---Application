# For: Database table definitions, indexes, triggers, and default seed data
# Must never: Alter or drop production tables without an explicit migration

import json
import uuid
from datetime import datetime, timezone
import sqlite3
from engine.app.core.config import settings
from engine.app.core.security import hash_password

DDL_STATEMENTS = """
CREATE TABLE IF NOT EXISTS users (
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

CREATE TABLE IF NOT EXISTS refresh_tokens (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS vacancies (
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

CREATE TABLE IF NOT EXISTS import_batches (
  id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  row_count INTEGER NOT NULL,
  error_count INTEGER NOT NULL,
  imported_by TEXT REFERENCES users(id),
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS import_templates (
  id TEXT PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  mapping_json TEXT NOT NULL,
  created_by TEXT REFERENCES users(id),
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS applications (
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

CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  application_id TEXT NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
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

CREATE TABLE IF NOT EXISTS document_pages (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  page_no INTEGER NOT NULL,
  width INTEGER,
  height INTEGER,
  image_path TEXT,
  ocr_text TEXT,
  UNIQUE(document_id, page_no)
);

CREATE TABLE IF NOT EXISTS model_versions (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  path TEXT NOT NULL,
  metrics_json TEXT,
  is_active INTEGER DEFAULT 1,
  installed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS extraction_runs (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  mode TEXT NOT NULL,
  model_version_id TEXT REFERENCES model_versions(id),
  started_at TEXT NOT NULL,
  total_ms INTEGER,
  timings_json TEXT,
  status TEXT,
  error_message TEXT,
  is_latest INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS extracted_fields (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES extraction_runs(id) ON DELETE CASCADE,
  document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
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

CREATE TABLE IF NOT EXISTS consistency_checks (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES extraction_runs(id) ON DELETE CASCADE,
  check_name TEXT NOT NULL,
  result TEXT NOT NULL,
  detail TEXT
);

CREATE TABLE IF NOT EXISTS review_items (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  reason TEXT NOT NULL,
  priority INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'open',
  assigned_to TEXT REFERENCES users(id),
  created_at TEXT NOT NULL,
  completed_at TEXT
);

CREATE TABLE IF NOT EXISTS field_reviews (
  id TEXT PRIMARY KEY,
  field_id TEXT NOT NULL REFERENCES extracted_fields(id) ON DELETE CASCADE,
  review_item_id TEXT REFERENCES review_items(id) ON DELETE CASCADE,
  reviewer_id TEXT NOT NULL REFERENCES users(id),
  decision TEXT NOT NULL CHECK (decision IN ('accepted','corrected','rejected')),
  corrected_value TEXT,
  comment TEXT,
  reviewed_at TEXT NOT NULL,
  used_for_training INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS eligibility_results (
  id TEXT PRIMARY KEY,
  application_id TEXT NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  vacancy_id TEXT NOT NULL REFERENCES vacancies(id),
  verdict TEXT NOT NULL,
  reasons_json TEXT,
  evaluated_at TEXT NOT NULL,
  is_latest INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS processing_jobs (
  id TEXT PRIMARY KEY,
  scope TEXT NOT NULL,
  vacancy_id TEXT REFERENCES vacancies(id),
  mode TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'queued',
  total INTEGER NOT NULL DEFAULT 0,
  done INTEGER NOT NULL DEFAULT 0,
  failed INTEGER NOT NULL DEFAULT 0,
  avg_ms INTEGER DEFAULT 0,
  created_by TEXT REFERENCES users(id),
  created_at TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT
);

CREATE TABLE IF NOT EXISTS job_items (
  id TEXT PRIMARY KEY,
  job_id TEXT NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
  document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  state TEXT NOT NULL DEFAULT 'queued',
  attempts INTEGER DEFAULT 0,
  error_message TEXT,
  ms INTEGER
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value_json TEXT NOT NULL,
  updated_by TEXT REFERENCES users(id),
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS reports (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  format TEXT NOT NULL,
  filters_json TEXT,
  file_path TEXT,
  created_by TEXT REFERENCES users(id),
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
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
"""

INDEX_STATEMENTS = """
CREATE INDEX IF NOT EXISTS idx_app_vacancy_status ON applications(vacancy_id, status);
CREATE INDEX IF NOT EXISTS idx_app_reg_no ON applications(registration_no);
CREATE INDEX IF NOT EXISTS idx_doc_app ON documents(application_id);
CREATE INDEX IF NOT EXISTS idx_doc_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_field_doc ON extracted_fields(document_id, field_name);
CREATE INDEX IF NOT EXISTS idx_field_run ON extracted_fields(run_id);
CREATE INDEX IF NOT EXISTS idx_job_items_job_state ON job_items(job_id, state);
"""

TRIGGER_STATEMENTS = """
CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit_log
BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;

CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit_log
BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;
"""


def init_db(conn: sqlite3.Connection) -> None:
    """Executes DDL statements, creates indexes and triggers, and seeds users."""
    conn.executescript(DDL_STATEMENTS)
    conn.executescript(INDEX_STATEMENTS)
    conn.executescript(TRIGGER_STATEMENTS)
    seed_default_users(conn)
    seed_default_settings(conn)


def seed_default_users(conn: sqlite3.Connection) -> None:
    """Seeds default accounts if the users table is empty."""
    cursor = conn.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] > 0:
        return
    now = datetime.now(timezone.utc).isoformat()
    defaults = [
        (str(uuid.uuid4()), "admin", "System Administrator", hash_password("Admin@123"), "admin", 1, now),
        (str(uuid.uuid4()), "officer1", "A. Kumar (Screening Officer)", hash_password("Officer@123"), "officer", 1, now),
        (str(uuid.uuid4()), "reviewer1", "P. Sharma (Reviewer)", hash_password("Reviewer@123"), "reviewer", 1, now),
    ]
    conn.executemany(
        "INSERT INTO users (id, username, full_name, password_hash, role, is_active, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?);",
        defaults
    )


def seed_default_settings(conn: sqlite3.Connection) -> None:
    """Seeds default configuration thresholds into settings table."""
    now = datetime.now(timezone.utc).isoformat()
    defaults = {
        "confidence_threshold_default": json.dumps(settings.confidence_threshold_default),
        "manual_minutes_per_doc": json.dumps(settings.manual_minutes_per_doc),
        "enabled_languages": json.dumps(settings.enabled_languages),
        "auto_accept_threshold": json.dumps(settings.auto_accept_threshold),
        "percentage_tolerance": json.dumps(settings.percentage_tolerance),
    }
    for k, v in defaults.items():
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value_json, updated_at) VALUES (?, ?, ?);",
            (k, v, now)
        )
