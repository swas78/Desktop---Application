<!-- For: Architectural and dependency design decision records (ADRs) -->
<!-- Must never: Omit rationale for non-obvious technology and library selections -->

# Architectural Decision Records (ADRs)

### ADR-01: Electron + React Desktop Shell with Localhost Python Engine
- **Decision**: Use an Electron desktop shell communicating with a bundled Python FastAPI engine over localhost rather than an in-process Python-JS bridge or web-hosted architecture.
- **Rationale**: RAC DRDO screening requires strict offline operation with no applicant PII leaving the local workstation. Python provides superior NLP, OCR, and ML processing libraries, while Electron provides a native desktop experience with hardware acceleration and file system isolation.

### ADR-02: SQLite with SQLCipher and Append-Only Audit Log
- **Decision**: Use SQLite with SQLCipher encryption at rest and append-only database triggers for the audit log.
- **Rationale**: Avoids external database daemon administration (e.g. PostgreSQL or MySQL) while ensuring zero unencrypted data rests on the physical machine. SHA-256 hash chaining ensures that any manual tampering with past audit records is immediately detectable.

### ADR-03: RapidFuzz for Candidate Name Matching
- **Decision**: Use RapidFuzz `token_set_ratio` instead of simple Levenshtein distance or soundex.
- **Rationale**: Indian candidate names frequently have varying token order, expanded or contracted initials (e.g., *"Rahul Kumar Sharma"* vs *"Rahul K Sharma"*), or prefixes (*"Shri"*, *"Km"*). `token_set_ratio` handles subset inclusion and token permutations cleanly with high C++ execution speed.

### ADR-04: ReportLab and OpenPyXL for Offline Reporting
- **Decision**: Generate PDF and Excel reports using ReportLab and openpyxl locally inside Python.
- **Rationale**: Eliminates dependencies on cloud PDF rendering APIs or external browser print services, operating seamlessly with the network cable disconnected.
