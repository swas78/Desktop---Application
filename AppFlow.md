App Flow
Product: Automated Document Verification System (ADVS), desktop application (Electron + React)
1. Navigation Map
Launch
  Splash (engine start, model warm-up)
    Login
      Main Shell (sidebar)
        Dashboard
        Applications
          Application Detail
        Instant Check
        Batch Processing
          Job Detail
        Review Queue
          Review Workbench
        Vacancies and Rules
        Reports
        Admin (Users, Settings, Models, Audit)
Sidebar items depend on role: Admin sees everything; Officer hides Admin; Reviewer sees Review Queue, Applications (read-only), Dashboard (read-only).
2. Screens and What They Contain
Screen
Purpose
Key elements
Splash
Start engine and load models
Progress bar, status text, retry on failure
Login
Authenticate
Username, password, error banner, lockout after 5 failures
Dashboard
Show efficiency and quality
KPI cards, throughput chart, mismatch breakdown, accuracy by document type, hours saved
Applications
Browse and import
Table (search, filters, status chips), Import button, bulk actions
Application Detail
One applicant end to end
Biodata panel, document list with status, field comparison table, eligibility verdict, history
Instant Check
Immediate single-document test
Drop zone, biodata form or picker, results panel with mismatch alerts
Batch Processing
Run verification at scale
Scope selector, mode (quick or deep), live progress, pause, resume, cancel
Review Queue
Work list for reviewers
Filters (type, reason, confidence), claim button, counts
Review Workbench
Resolve one document
Document viewer with boxes (left), field list (right), accept, edit, reject, next
Vacancies and Rules
Define criteria
Vacancy list, rule editor, test-against-sample button
Reports
Export outcomes
Report type, filters, format, generate, history
Admin
System control
Users and roles, thresholds, languages, model versions, audit log viewer
3. Core Flows
Flow A: Launch and Login
1. User opens the app; Electron main process starts the Python engine on a random localhost port.
2. Splash shows engine health; models load in the background.
3. If health check fails, show an error with Retry and View Log.
4. User logs in; role is read from the token; the shell loads with the matching sidebar.
Flow B: Instant Check (the submission-time alert)
1. Officer opens Instant Check.
2. Drops a PDF or image; optionally selects the document type; enters or selects the biodata values to compare.
3. App sends the file to /verify/instant.
4. Quality gate fails: show "Image too blurry, please re-upload" and stop. Otherwise continue.
5. Results appear in 3 seconds or less: document type, extracted fields beside form values, each marked Match, Mismatch, or Low confidence.
6. Mismatch alert banner lists each difference in plain language.
7. Officer can export the alert text for the applicant, save to the application, or send the case to review.
Flow C: Import Applications
1. Applications screen, then Import.
2. Choose a CSV/Excel/JSON file; map columns (saved as a template for reuse).
3. App validates rows and shows a preview with errors highlighted.
4. Confirm: records are created.
5. Link documents: pick the folder of uploaded files; the app matches by registration number in file names and reports unmatched files.
Flow D: Batch Screening
1. Batch Processing, then New Job.
2. Choose scope (vacancy, selected applications, all pending) and mode: Quick (default) or Deep (more robust extraction, used during screening).
3. Start: documents enter the queue; the progress view streams live counts, average time, and failures.
4. Each document ends as Verified (all fields auto-accepted and matching), Mismatch, or Needs Review.
5. Officer can pause, resume, cancel, or retry failures.
6. On completion, the eligibility engine runs and application statuses update; a summary appears with a link to the Review Queue.
Flow E: Review
1. Reviewer opens the Review Queue and claims an item (or uses Next Item).
2. Workbench shows the original document with the extracted field regions highlighted; selecting a field jumps to its region.
3. For each flagged field: Accept, Correct (type the right value), or Reject (document is invalid or unreadable).
4. Add an optional comment; keyboard shortcuts: A accept, E edit, R reject, N next.
5. Complete the item: the application status and eligibility are recomputed; the correction is saved as training data.
Flow F: Eligibility and Vacancy Setup
1. Admin opens Vacancies and Rules, then New Vacancy.
2. Enters advertisement details and rules (qualification, branches, minimum marks, age limits by category, required documents).
3. Runs Test Against Sample to preview the verdicts.
4. Saves; rules apply to later evaluations and can be re-run in bulk.
Flow G: Dashboard and Reports
1. Dashboard loads KPI summary and charts for a selected date range.
2. Click a chart segment (for example, a mismatch type) to drill down to the matching applications.
3. Reports: choose type, filters, and format (PDF or Excel); generate; download or open the folder.
Flow H: Administration
1. Users: create, assign roles, deactivate, reset passwords.
2. Settings: confidence thresholds, language packs, minutes saved per manual check.
3. Models: view versions, activate or roll back.
4. Audit: filter by user, action, and date; export.
4. Document Status State Machine
uploaded -> quality_failed (terminal; user must re-upload)
uploaded -> queued -> processing -> verified
                                  -> mismatch
                                  -> needs_review -> (reviewer) -> verified | mismatch | rejected
processing -> failed -> (retry) -> queued
Application status is derived from its documents: verified only if all required documents are verified and eligibility is not negative; any needs_review document makes it needs_review; any rejected required document makes it rejected.
5. Field Result Colors and Labels
Status
Color
Meaning
Next action
Match
Green
Document agrees with form
None
Mismatch
Red
Values differ
Review or notify applicant
Low confidence
Amber
Engine unsure
Review
Not found
Grey
Field missing in document
Review
6. Error and Edge-Case Handling
Situation
Behaviour
Engine not responding
Banner with auto-restart attempt; jobs resume from the persisted queue
Unsupported or corrupt file
Reject with a clear reason; keep a log entry
Password-protected PDF
Ask for password or mark for manual handling
Multi-document PDF
Split by detected document type and ask to confirm
Non-English or non-Hindi document
Auto-detect language; show original and translated text side by side
Handwritten content
Mark Needs Review
Token expired
Silent refresh; if it fails, return to Login without losing in-progress review edits
Disk nearly full
Warn before starting batches
7. Optional Mobile Companion (React Native)
1. Applicant or officer opens the scanner and captures the document.
2. App checks edge detection, blur, glare, and resolution on the device.
3. If poor, it prompts a retake; if good, it uploads or exports the file for the desktop system.
4. The same instant-check response format can be shown when the device is connected to the engine on the local network.
8. Demo Script (3 minutes)
1. Log in and show the Dashboard.
2. Instant Check with a marksheet where the percentage was altered: highlight the mismatch alert in under 3 seconds.
3. Drop a Hindi-language certificate: show OCR, translation, and extracted fields.
4. Run a batch of 200 applications: show live throughput.
5. Open a Needs Review item in the workbench and correct a field.
6. Return to the Dashboard to show updated accuracy, review rate, and hours saved.