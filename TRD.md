Technical Requirements Document (TRD)
Product: Automated Document Verification System (ADVS), desktop application Version: 1.0 | Status: Draft
1. Technical Summary
ADVS is an Electron + React desktop application that talks over localhost to a bundled Python AI engine (FastAPI). The engine runs the document pipeline (preprocess, classify, OCR, extract, verify). All data is stored locally in an encrypted SQLite database. The system runs fully offline.
React Native is used only for an optional mobile companion (document capture and quality check) that shares TypeScript types with the desktop app. React Native is not used for the desktop shell.
2. Architecture
Electron App
  Renderer (React + TS)  <--IPC (contextBridge)-->  Main Process (Node.js)
                                                      |
                                                      | HTTP (127.0.0.1) + WebSocket
                                                      v
                                        Python Engine (FastAPI + Uvicorn)
                                          Pipeline workers (process pool)
                                                      |
                                                      v
                                    SQLite (SQLCipher) + encrypted file store
Components
Component
Responsibility
Renderer (React)
All UI: screens, tables, charts, document viewer
Main process
Window lifecycle, spawning and supervising the engine, file dialogs, secure IPC, auto-update, token storage
Preload script
Exposes a minimal, typed API to the renderer (context isolation on, node integration off)
Python engine
REST API, job queue, ML pipeline, rule engine, database access
Worker pool
Parallel document processing (multiprocessing), models loaded once per worker
Storage
SQLite with SQLCipher, document files encrypted on disk
3. Technology Stack
Layer
Technology
Notes
Shell
Electron (current LTS), electron-builder
Windows NSIS installer first
UI
React 18, TypeScript, Vite

Styling
Tailwind CSS or MUI

State
Zustand or Redux Toolkit; TanStack Query for server state

Tables
TanStack Table (virtualized)
Large batch lists
Charts
Apache ECharts
Dashboard
Viewer
pdf.js (react-pdf), canvas overlay
Bounding boxes
Engine
Python 3.11, FastAPI, Uvicorn, Pydantic v2

Queue
In-process job queue (asyncio + multiprocessing), persisted in DB
No external broker needed
PDF / images
PyMuPDF, OpenCV, Pillow

OCR
PaddleOCR (primary), Tesseract with Indic packs (fallback)
Ensemble optional
Doc models
LayoutLMv3 or Donut fine-tuned, exported to ONNX
ONNX Runtime / OpenVINO
Classification
EfficientNet-B0 or MobileNetV3 (image) + keyword classifier

NLP
spaCy, RapidFuzz, IndicTrans2 / Argos (translation), Indic transliteration

Codes
pyzbar / zxing-cpp
QR and barcode
Database
SQLite + SQLCipher (single user); PostgreSQL option for LAN multi-user

Auth
bcrypt, JWT (short-lived)

Reports
ReportLab or WeasyPrint (PDF), openpyxl (Excel)

Packaging
PyInstaller (engine), electron-builder
Single installer
Testing
pytest, Jest, React Testing Library, Playwright (Electron)

Mobile (optional)
React Native, VisionCamera, document-scanner library
Capture and quality check
4. Processing Pipeline Specification
Stage
Input
Output
Target time
1. Ingest and quality check
File
Page images, quality score
0.2 s
2. Preprocess
Page images
Deskewed, denoised image
0.3 s
3. Classify
Image + quick OCR snippet
Doc type + confidence
0.2 s
4. QR / barcode decode
Image
Decoded payload if present
0.1 s
5. OCR
Image
Text boxes, per-word confidence
0.8 s
6. Language detect and translate
Text
English text, original kept
0.3 s (only if non-EN/HI)
7. Field extraction
Boxes + text + image
Typed fields with confidence and bboxes
0.5 s
8. Verification
Fields + biodata
Per-field status, risk flags
0.1 s
Total


about 2.5 s, 3 s hard budget
Confidence policy
• Field confidence = combination of OCR confidence, model confidence, format validity, and cross-source agreement (QR, second OCR engine).
• Auto-accept if confidence is at or above the threshold (default 0.97, configurable per field); below that, send to the review queue.
• Accuracy is reported on auto-accepted fields; the review rate is reported separately.
5. Verification Rules
• Name: normalize case and punctuation, expand initials, transliterate, then token-set fuzzy ratio. At least 90 is Match; 75 to 89 is Low confidence; below 75 is Mismatch.
• Date: parse several formats into ISO; exact equality.
• Marks: sum of subject marks must equal total; percentage recomputed with tolerance of 0.01; CGPA to percentage conversion rule configurable per university.
• Identifiers: format regex per issuer; QR payload equality where available.
• Validity: EWS valid for the financial year of application; GATE score valid 3 years from result; certificate issue date at or before the closing date.
• Eligibility: rule set per vacancy stored as JSON (qualification, minimum marks, age with category relaxations, experience).
6. Performance Strategy
• Persistent engine; models loaded at startup and kept warm.
• ONNX Runtime with graph optimization; INT8 quantization where accuracy loss is under 0.2%.
• Classification first, then only the matching extractor.
• Downscale detection input; crop to regions for recognition.
• Process pool sized to cores minus one; pages of one document run in parallel.
• Use GPU (CUDA or DirectML) when detected.
• Benchmark harness in CI: fails the build if p95 exceeds 3 s on the reference machine.
7. Accuracy Strategy and Measurement
• Golden test set of at least 500 annotated documents per major type (synthetic plus anonymized real), split into train, validation, test.
• Metrics: field-level exact-match accuracy, character error rate, classification accuracy, auto-accept precision, review rate.
• Three Sigma target applies to auto-accepted fields: error rate at or below 0.27%.
• Active learning: reviewer corrections are exported as training data; models are retrained and versioned.
8. Security Requirements
• Electron: contextIsolation on, nodeIntegration off, sandbox on, strict CSP, no remote content.
• Engine binds to 127.0.0.1 only, with a random per-launch port and a bearer token passed by the main process.
• SQLCipher database; key derived from user passphrase (Argon2id) or Windows DPAPI.
• Documents encrypted on disk (AES-256-GCM).
• Passwords hashed with bcrypt; role-based access control enforced in the engine, not only the UI.
• Append-only audit log with hash chaining to detect tampering.
• No telemetry; no network calls by default; optional connectors are off unless an admin enables them.
• Code-signed installer; dependency pinning and vulnerability scanning.
9. Deployment and Environment
Item
Spec
OS
Windows 10/11 64-bit (primary)
Minimum
4 cores, 8 GB RAM, 10 GB disk
Recommended
8 cores, 16 GB RAM, NVIDIA GPU optional
Install
Single signed installer; models and language packs bundled or as optional add-ons
Updates
Offline update package (signed)
10. Project Structure
advs/
  apps/
    desktop/            Electron main, preload, React renderer
    mobile/             React Native companion (optional)
  packages/
    shared-types/       TypeScript types, API client
  engine/
    app/
      api/              FastAPI routers
      core/             config, security, logging
      pipeline/         preprocess, classify, ocr, extract, verify
      rules/            eligibility and validation rules
      db/               models, migrations (Alembic)
      workers/          job queue and pool
    models/             ONNX models, language packs
    tests/
  tools/                synthetic data generator, benchmark harness
  docs/
11. Testing Strategy
Level
Tools
Scope
Unit
pytest, Jest
Rules, parsers, matchers, components
Integration
pytest + test client
API plus DB plus pipeline on fixtures
E2E
Playwright for Electron
Import, process, review, export flows
Performance
Custom harness
p50 and p95 per document type
Accuracy
Evaluation scripts
Golden set metrics per release
Security
Bandit, npm audit, manual review
Static and dependency scans
12. Logging and Monitoring
• Structured JSON logs rotated locally; no PII in logs (field values masked).
• Per-document timing breakdown stored for the dashboard.
• Model version recorded with every result for reproducibility.
13. Technical Risks
Risk
Mitigation
3 s budget on CPU-only machines
Quantized ONNX, early exits, GPU optional, skip translation unless needed
Engine crash
Supervisor restarts it; jobs are persisted and resumed
Large installer size
Optional language packs, quantized models
Model drift on new templates
Review loop, retraining pipeline, versioned rollout