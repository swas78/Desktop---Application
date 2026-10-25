<!-- For: High-level architectural specifications, component boundaries, and security model -->
<!-- Must never: Omit offline data boundaries or bypass tamper-evident audit specifications -->

# ADVS Architecture

## 1. Overview
The Automated Document Verification System (ADVS) is built around a two-process desktop architecture running entirely offline on localhost.

```
+-------------------------------------------------------------------------------+
| ELECTRON DESKTOP SHELL                                                        |
|                                                                               |
|  +--------------------------------+       ContextBridge IPC                   |
|  | React 18 Renderer (TypeScript) | <----------------------------+            |
|  | - Verification Desk UI         |                              |            |
|  | - Review Workbench            |                              v            |
|  | - Primary Ledger Dashboard     |                    +--------------------+ |
|  +--------------------------------+                    | Electron Main      | |
|                 |                                      | Process Supervisor | |
|                 | HTTP (127.0.0.1) + WebSocket         +--------------------+ |
+-----------------|------------------------------------------------|------------+
                  v                                                | Spawns with
+-------------------------------------------------------+          | token
| PYTHON FASTAPI ENGINE                                 |<---------+
|                                                       |
|  +-------------------------------------------------+  |
|  | API Layer (auth, verify, jobs, review, reports) |  |
|  +-------------------------------------------------+  |
|                         |                             |
|                         v                             |
|  +-------------------------------------------------+  |
|  | 9-Stage Document Processing Pipeline            |  |
|  | Ingest -> Preprocess -> OCR -> Classify ->      |  |
|  | QRDecode -> Translate -> Extract -> Verify      |  |
|  +-------------------------------------------------+  |
|                         |                             |
|                         v                             |
|  +-------------------------------------------------+  |
|  | Eligibility & Validation Rules Engine           |  |
|  +-------------------------------------------------+  |
+-------------------------|-----------------------------+
                          v
+-------------------------------------------------------+
| LOCAL SECURE STORAGE                                  |
| - SQLite with Foreign Keys & Trigger Immutability     |
| - Tamper-evident Hash-Chained Audit Log               |
| - AES-256-GCM Encrypted Document File Vault           |
+-------------------------------------------------------+
```

## 2. Component Boundaries
1. **Renderer (React 18 + TypeScript)**:
   - Contains all user-facing verification desk screens, review workbench, tables, and charts.
   - Enforces context isolation (`contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`).
   - Talks only to `127.0.0.1` via the single API client wrapper `advsApi`.
2. **Main Process (Electron)**:
   - Supervises the Python engine lifecycle. Spawns it with a random per-launch authentication token.
   - Restarts the engine if unexpected termination occurs.
3. **Python Engine (FastAPI + Uvicorn)**:
   - Hosts the REST API and WebSocket progress broadcaster.
   - Runs the 9-stage verification pipeline under a hard 3.0s latency budget.
   - Evaluates eligibility rules deterministically in `engine/app/rules/`.
4. **Data & Security Layer**:
   - SQLite database storing applications, vacancies, extraction runs, and review queues.
   - `audit_log` with SHA-256 hash chaining and SQLite abort triggers blocking UPDATE and DELETE.
   - Document files stored encrypted with AES-256-GCM on disk.
