Product Requirements Document (PRD)
Product: Automated Document Verification System (ADVS), a desktop application Client / Context: Recruitment and Assessment Centre (RAC), DRDO, Ministry of Defence (SIH 2024 problem statement) Version: 1.0 | Status: Draft
1. Overview
RAC receives online biodata applications with supporting documents (educational certificates, marksheets, GATE scorecards, experience letters, caste, EWS and PwD certificates) as images or PDFs, sometimes in languages other than English or Hindi. Verification is manual, slow, and error-prone. ADVS uses Intelligent Document Processing (OCR, ML, NLP) to extract data from documents, compare it with the applicant biodata, flag mismatches, and present efficiency metrics on a dashboard.
2. Goals and Non-Goals
Goals
• Automatically extract key fields from submitted documents.
• Verify extracted data against biodata and flag mismatches (Match / Mismatch / Low confidence).
• Provide an immediate-check mode (at submission) and a deeper screening mode (during shortlisting).
• Reach Three Sigma accuracy (99.73%) on auto-accepted fields.
• Process each document in 3 seconds or less.
• Show results and efficiency gains on a BI dashboard.
• Operate offline, with local encrypted storage.
Non-Goals (v1)
• Replacing the recruitment portal itself.
• Fully automated final selection decisions (humans stay in the loop).
• Handwritten-document recognition beyond routing to review.
3. Users and Personas
Persona
Description
Key needs
Admin
Configures vacancies, rules, users, thresholds
Control, audit visibility
Screening Officer
Runs batch verification on applications
Speed, clear flags, exports
Reviewer
Resolves low-confidence and mismatched cases
Side-by-side view, fast correction
Applicant (indirect)
Receives mismatch alerts
Clear, actionable messages
4. User Stories
1. As a Screening Officer, I import applications and documents in bulk so that verification starts without manual data entry.
2. As a Screening Officer, I drop a single document and see extracted fields next to biodata values, so mismatches are obvious instantly.
3. As a Reviewer, I see the original document with highlighted regions beside extracted values, so I can accept or correct in one click.
4. As an Admin, I define vacancy criteria (qualification, minimum marks, age, category relaxations) so eligibility is evaluated automatically.
5. As an Admin, I set confidence thresholds and manage users and roles.
6. As a Manager, I view a dashboard of throughput, accuracy, and hours saved.
7. As an Officer, I export verification reports and shortlists as PDF or Excel.
8. As an Applicant (via portal integration or notification export), I get a mismatch alert listing which fields differ.
5. Functional Requirements
FR-1 Ingestion
• Accept PDF, JPG, PNG, TIFF; multi-page PDFs supported.
• Import biodata from CSV or Excel or JSON; map columns via a configurable template.
• Reject poor-quality uploads (blur, darkness, low resolution) with a reason.
FR-2 Classification
• Identify document type: 10th/12th marksheet, degree/provisional certificate, GATE scorecard, experience letter, caste, EWS, PwD, other.
• Unknown types go to manual review.
FR-3 Extraction
• OCR with Hindi, English, and configurable Indic language packs.
• Field extraction per document type (see field catalogue below).
• Read QR codes or barcodes where present and use them as high-confidence ground truth.
FR-4 Verification
• Field-level comparison with fuzzy name matching, normalized dates, numeric tolerance.
• Internal consistency checks (subject marks sum to total, percentage recomputation).
• Validity rules (EWS certificate financial-year validity, GATE score validity window, certificate issue date vs. closing date).
• Per-field status plus per-document and per-application summary.
FR-5 Authenticity checks
• Detect metadata anomalies, inconsistent fonts or compression, and missing or altered seals (heuristic; flagged as risk score, not as proof).
• Optional online verification connectors (DigiLocker or similar) when permitted.
FR-6 Review workbench
• Source document viewer with bounding boxes, zoom, rotate.
• Accept, edit, or reject each field; comments; audit trail.
• Corrections stored as labelled data for future retraining.
FR-7 Eligibility engine
• Vacancy definitions with configurable rules; result Eligible / Not Eligible / Needs Review with reasons.
FR-8 Batch processing
• Queue with progress, pause, resume, retry; per-document timing.
FR-9 Dashboard and reports
• Metrics: documents processed, average and p95 time, auto-verified rate, review rate, mismatch categories, accuracy trend, estimated hours saved.
• Export to PDF and Excel.
FR-10 Administration and security
• Role-based access, bcrypt-hashed credentials, encrypted local storage, immutable audit log.
• Settings for language packs, thresholds, model version.
6. Field Catalogue (initial)
Document
Fields
10th / 12th marksheet
Name, father or mother name, DOB, roll number, board, year, subjects and marks, total, percentage or CGPA, result
Degree / marksheet
Name, university, degree, branch, roll or enrolment number, year, CGPA or percentage, class
GATE scorecard
Name, registration number, paper, year, GATE score, AIR, marks, validity
Experience letter
Name, organization, designation, from-date, to-date, issuer
Caste certificate
Name, parent name, caste and category, issuing authority, certificate number, issue date, state
EWS certificate
Name, income, financial year, issuing authority, date
PwD certificate
Name, disability type, percentage, issuing authority, validity
7. Non-Functional Requirements
Area
Requirement
Accuracy
At least 99.73% field accuracy on auto-accepted fields; measured per field and per document type on a held-out test set
Speed
3 seconds or less per document (single page, standard hardware, steady state)
Availability
Works fully offline
Security
Local AES-256 encryption at rest, role-based access, audit log, no external data transfer by default
Scalability
10,000+ applications per batch run without UI freezing
Usability
Keyboard shortcuts in review, English UI, accessible contrast
Portability
Windows 10 or 11 first; Linux and macOS best-effort
Maintainability
Versioned models, schema migrations, structured logs
8. Success Metrics
• Auto-accepted field accuracy at or above 99.73%.
• Median processing time at or below 2 s, p95 at or below 3 s.
• At least 70% of documents fully auto-verified; remainder routed to review.
• At least 80% reduction in manual verification time per application.
• Reviewer correction rate trending downward release over release.
9. Assumptions and Dependencies
• Applicant documents and biodata can be exported from the RAC portal.
• Sample documents are available for tuning (anonymized).
• Hardware: 8 GB or more RAM, 4 or more CPU cores; optional GPU.
• Online verification APIs need separate government approval, so they are optional.
10. Risks
Risk
Mitigation
Many board and university templates
Layout-aware models plus review fallback; add templates incrementally
Handwriting and poor scans
Quality gate; route to review
Three Sigma claim is hard on messy data
Confidence thresholds, QR and consistency checks, honest per-field reporting
Sensitive data
Offline processing, encryption, audit trail
Large installer
Quantized models, optional language packs
11. Release Plan
• MVP (weeks 1-6): single-document check, 4 document types, mismatch UI, QR reading.
• v1.0 (weeks 7-10): batch screening, review workbench, eligibility engine, dashboard, reports.
• v1.1: more languages, authenticity checks, optional React Native scanner companion, online verification connectors.
12. Open Questions
1. Exact biodata export format from the RAC portal?
2. Which languages beyond Hindi and English are priority?
3. Single-user desktop or multi-user over LAN?
4. Are official verification APIs accessible in the deployment environment?