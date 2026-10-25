<!-- For: ADVS top-level project overview, system requirements, and setup instructions -->
<!-- Must never: Direct users to external online servers or expose production keys -->

# Automated Document Verification System (ADVS)
### Recruitment and Assessment Centre (RAC), DRDO

ADVS is an offline, privacy-first desktop application designed for government recruitment screening officers. It automatically ingests candidate applications and supporting certificates (educational marksheets, GATE scorecards, category certificates), extracts typed fields, compares values against candidate biodata, and validates candidate eligibility against vacancy rules with Three Sigma accuracy (&ge; 99.73% on auto-accepted fields) in under 3.0 seconds per document.

---

## 1-Command Startup (Recommended)

Run the automated launcher script from the root of the project:
```bash
./run.sh
```
*Or via npm:*
```bash
npm start
```
This automatically verifies the Python environment, starts the backend FastAPI engine in the background on `127.0.0.1:8000`, waits for the health check to pass, and opens the verification desk interface. Exiting the terminal cleanly stops both services.

To run the automated quality gates (tests, latency benchmark, and Three Sigma accuracy evaluation):
```bash
npm test
```

---

## Default Operator Credentials
- **Administrator**: `admin` / `Admin@123`
- **Screening Officer**: `officer1` / `Officer@123`
- **Reviewer**: `reviewer1` / `Reviewer@123`

---

## 4 Streamlined Verification Workspaces
1. **Verification Desk**: Instant single document check with 1-click sample presets (clean marksheet, altered percentage, blurry scan), visible &le; 3.0s timer, sequential stamp animations, and discrepancy alerts.
2. **Review Workbench**: Dedicated human-in-the-loop review queue and side-by-side document examination with examiner margin notes, leader lines, and keyboard shortcuts (`A` Accept, `E` Edit, `R` Reject, `N` Next).
3. **Applications & Screening**: Complete candidate registry with search, status filters, and 1-click batch screening runner.
4. **Ledger & Administration**: Primary verification ledger, hours saved calculator, formal PDF/Excel report exports, vacancy rules, and tamper-evident SHA-256 audit log.

---

## macOS DMG Packaging & Submission

To build the Apple Disk Image (`.dmg`) for submission:

```bash
npm run dist:dmg
```
*Or:*
```bash
npm run package
```

The compiled installer is generated at:
```
apps/desktop/release/ADVS-1.0.0-arm64.dmg
```

### Installing and Running from DMG
1. Double-click `ADVS-1.0.0-arm64.dmg`.
2. Drag `ADVS.app` into the `Applications` folder.
3. Launch `ADVS` from Applications or Spotlight.
4. *Gatekeeper note*: Because this is an air-gapped test build without a paid Apple Developer certificate, if macOS shows a security prompt on first launch, right-click `ADVS.app` and select **Open**, or run `xattr -cr /Applications/ADVS.app`.


