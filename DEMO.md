<!-- For: Step-by-step 3-minute demonstration script for presentation and evaluators -->
<!-- Must never: Omit sample document references or fail to present intentional error handling -->

# ADVS 3-Minute Demonstration Script

This script guides evaluators and recruitment officers through the streamlined end-to-end verification flow using the pre-generated sample files.

---

## Preparation (1-Click Startup)
Launch the complete application (both Python engine and desktop shell) with a single command:
```bash
./run.sh
```
*(or `npm start`)*

---

## 3-Minute Walkthrough Flow

### 0:00 - 0:30: Sign In & Verification Desk Overview
1. At the **Splash Screen**, observe the automated engine health check and model warm-up.
2. Sign in as `officer1` (Password: `Officer@123`).
3. Land directly on the **Verification Desk**, equipped with 1-click testing presets.

### 0:30 - 1:15: Instant Check with 1-Click Preset (< 3.0 Seconds)
1. In the **Verification Desk**, click the button: **1-Click: Altered Marksheet**.
2. Notice the results appear in under **0.5 seconds** (passing the 3.0s budget):
   - Timer displays exact processing duration (e.g. `0.021 s`).
   - Stamp marks land sequentially on extracted fields.
   - Discrepancy banner immediately highlights the mismatch:  
     *"Discrepancy alert for applicant: Percentage: entered '74.20' but document shows '72.4'."*
3. Click the **Review in workbench** button right inside the alert banner to transition directly into the human review workspace.

### 1:15 - 1:45: Quality Gate Defense (Blurry Scan Rejection)
1. Return to the **Verification Desk**.
2. Click **1-Click: Blurry Scan (Quality Rejection)**.
3. The system intercepts the unreadable scan at Stage 1:
   - Clear, polite, actionable message:  
     *"Quality Gate Intercepted: This scan is too blurry to read. Upload a sharper copy."*
   - Proves the system gracefully handles real-world imperfect documents.

### 1:45 - 2:20: Applications & 1-Click Batch Screening
1. Click **Applications & Batch** in the left rail.
2. Notice candidate applications listed with category, eligibility, and verification status.
3. Click **Run batch screening** directly in the top header:
   - Queues pending documents and runs asynchronous batch verification.
   - Candidate statuses and eligibility update seamlessly.

### 2:20 - 2:50: Review Workbench & Examiner Margin Notes
1. Navigate to **Review Workbench** in the left rail.
2. Select any open item and click **Claim & Review**.
3. In the **Review Workbench**:
   - Document sits in the center on the examination table surface.
   - Examiner **margin notes** are joined to document bounding boxes by thin leader lines.
   - Demonstrate the keyboard shortcuts:
     - Press `A` to accept a field.
     - Press `E` to edit and correct a value.
     - Press `R` to reject an invalid entry.
     - Press `N` to jump to the next field.
   - Click **Complete review**.

### 2:50 - 3:00: Primary Ledger & Audit Verification
1. Navigate to **Ledger & Admin** in the left rail.
2. Under **Primary Verification Ledger**, point out:
   - Grouped document rows with auto-verified, sent-to-review, mismatches, and time-per-doc columns.
   - Hover over **Hours saved** to show the verifiable formula: `(auto_verified * 4 min) / 60`.
3. Switch to the **Audit Trail** tab (as `admin` / `Admin@123`):
   - Show the green badge confirming the SHA-256 cryptographic hash chain remains unbroken and untampered.
