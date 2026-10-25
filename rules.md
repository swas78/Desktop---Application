# ADVS Project Rules

Rules for everyone who writes code, designs screens, or presents this project.
Keep this file at the repository root. If a rule here conflicts with a habit, the rule wins.

**Project:** Automated Document Verification System (ADVS) for RAC, DRDO
**Stack:** Electron + React (TypeScript) desktop shell, Python (FastAPI) engine, SQLite
**Optional:** React Native companion app for document capture only

---

## 1. The five principles

1. **It must work before it looks good.** A feature is not done until it runs end to end on a clean machine.
2. **Simple beats clever.** If a teammate cannot explain a function after reading it once, rewrite it.
3. **Honest numbers.** Every accuracy and speed claim comes from a script in the repo, not from memory.
4. **Offline and private by default.** No applicant data leaves the machine. No telemetry.
5. **Designed for this job.** The interface looks like a verification desk for government recruiters, not a generic dashboard template.

---

## 2. Code that is easy to read and easy to present

The project will be read by judges and teammates who did not write it. Write for them.

### 2.1 Naming

- Names say what a thing is or does: `compareNames`, `extractMarksheetFields`, `ReviewQueueTable`.
- No abbreviations except the common ones: `id`, `url`, `ocr`, `qr`, `dob`.
- Booleans start with `is`, `has`, `can`: `isAutoAccepted`, `hasQrCode`.
- Constants are `UPPER_SNAKE_CASE` (Python) or `UPPER_SNAKE_CASE` in `constants.ts`.
- Python: `snake_case` for functions and files. TypeScript: `camelCase` for functions, `PascalCase` for components and types, `kebab-case` for file names of non-components.

### 2.2 Size limits

| Thing | Limit |
|---|---|
| Function | 40 lines. If longer, split it. |
| File | 300 lines. If longer, split by responsibility. |
| React component | One job. If it fetches, transforms, and renders, split into hook + view. |
| Function arguments | 4. More than that, pass an object. |
| Nesting depth | 3 levels. Use early returns. |

### 2.3 Comments

- Comment **why**, not what. The code already shows what.
- Every file starts with a two-line header: what this file is for, and what it must never do.
- Every pipeline stage has a short docstring with input, output, and the time budget.

```python
def verify_percentage(extracted: float, expected: float) -> FieldStatus:
    """Compare marks percentage from document with the form value.

    Tolerance is 0.01 because some boards round the printed percentage.
    """
```

### 2.4 One way to do each thing

- One HTTP client wrapper in the desktop app. Screens never call `fetch` directly.
- One place for thresholds: the `settings` table with defaults in `engine/app/core/config.py`.
- One place for verification rules: `engine/app/rules/`. No rule logic inside API routes or React components.
- One type definition per API object, in `packages/shared-types`. The UI and the engine agree on it.

### 2.5 Error handling

- Never swallow an error silently. Log it with context, then return a clear result.
- User-facing errors say what happened and what to do next (see section 6.6).
- A failed document never stops a batch. Mark it `failed`, record the reason, continue.

### 2.6 Folder layout

Follow the structure in the TRD. New code goes in the folder that matches its job:

```
apps/desktop/        Electron main, preload, React screens
packages/shared-types/
engine/app/api/      Routes only. No business logic.
engine/app/pipeline/ preprocess, classify, ocr, extract, verify
engine/app/rules/    Eligibility and validation rules
engine/app/db/       Models and migrations
tools/               Synthetic data and benchmark scripts
```

### 2.7 Dependencies

- Add a library only if it saves real work and is actively maintained.
- Pin exact versions. Record why a non-obvious library was chosen in `docs/decisions.md`.
- No library that needs the internet at runtime.

---

## 3. Definition of Done

A task is done only when **all** of these are true:

- [ ] It runs on a clean Windows install using the packaged installer, not only in the dev environment.
- [ ] It works with the network cable unplugged.
- [ ] Unit tests cover the new logic, and all existing tests pass.
- [ ] No console errors or Python tracebacks during normal use.
- [ ] Empty, loading, error, and large-data states are handled in the UI.
- [ ] A bad file (corrupt, blank, password-protected, wrong type) gives a clear message and no crash.
- [ ] Keyboard-only use works for the main path.
- [ ] The change is described in the pull request in plain words, with a screenshot for UI changes.
- [ ] Another person has reviewed it.

---

## 4. Quality gates (the project must work perfectly)

"Perfectly" means these gates pass on every release build. If one fails, we do not ship.

| Gate | Requirement | How it is checked |
|---|---|---|
| Speed | p95 at or below 3.0 s per single-page document on the reference machine | `tools/benchmark.py`, run in CI |
| Accuracy | Auto-accepted fields at or above 99.73% correct on the held-out test set | `tools/evaluate.py` |
| Review rate | Reported next to accuracy, never hidden | Same script |
| Stability | 5,000-document batch finishes with no crash and no memory growth beyond 20% | Soak test |
| Recovery | Killing the engine mid-batch loses no completed work; it resumes | Integration test |
| Security | No high-severity findings from `npm audit`, `pip-audit`, `bandit` | CI |
| Packaging | Installer installs, launches, processes a sample, and uninstalls cleanly | Manual checklist |

### 4.1 Accuracy reporting rules

- Report accuracy **per field and per document type**, never one blended number.
- The test set is never used for training or threshold tuning.
- Say how many documents were tested. A claim on 20 documents is not a claim.
- Three Sigma applies to **auto-accepted** fields. Documents routed to review are counted separately.
- If a number is below target, show it as it is and explain the plan. Do not adjust the data to hide it.

### 4.2 Test layers

| Layer | Tool | What it proves |
|---|---|---|
| Unit | pytest, Jest | Rules, parsers, matchers behave correctly |
| Integration | pytest with test client | API, database, and pipeline work together |
| End to end | Playwright for Electron | Import, process, review, export work on screen |
| Performance | `tools/benchmark.py` | Speed target holds |
| Accuracy | `tools/evaluate.py` | Accuracy target holds |

---

## 5. Data, security, and privacy rules

- Use only anonymised or synthetic documents in the repository. Real applicant files are never committed.
- Electron: `contextIsolation` on, `nodeIntegration` off, `sandbox` on, strict content security policy, no remote content.
- The engine listens on `127.0.0.1` only, on a random port, with a per-launch token.
- Database encrypted (SQLCipher). Document files encrypted on disk.
- Logs contain ids and field names, never personal values.
- Every login, upload, edit, review decision, and export is written to the append-only audit log.
- Role checks happen in the engine. Hiding a button in the UI is not security.
- Optional online connectors (for example, certificate verification services) are off until an Admin turns them on.

---

## 6. UI and design rules

The interface must not look like a template or like something a tool generated in one pass. It should look like it was made for people who check documents all day.

### 6.1 Design idea: the verification desk

Recruiters compare paper against a form. The interface keeps that picture: the **document is the centre of the screen**, and the app's marks around it work like an examiner's margin notes.

- The one memorable element is the **review workbench**: the document sits on a slightly lighter "table" surface. Each extracted field has a margin note beside the page, joined to its region on the document by a thin leader line. Status appears as a stamp-style mark on the note.
- Everything else stays quiet and disciplined. Spend the boldness in this one place.

### 6.2 Colour

Use these tokens. Define them once as CSS variables.

| Token | Hex | Use |
|---|---|---|
| `--desk` | `#E8ECEA` | App background (cool grey-green, not cream) |
| `--sheet` | `#F7F9F8` | Document surface and panels |
| `--ink` | `#17283F` | Text and primary actions (deep navy, not black) |
| `--steel` | `#5A6B7B` | Secondary text, borders |
| `--verified` | `#1E6B57` | Match |
| `--stamp` | `#A8322D` | Mismatch |
| `--caution` | `#B9801A` | Low confidence |

Rules:

- Status colours are used **only** for status. Never as decoration.
- Status is never shown by colour alone. Pair it with a word or shape (Match, Mismatch, Check).
- Contrast: body text at least 4.5:1, large text and icons at least 3:1.
- No gradients. No glow. No frosted-glass panels.
- Do not use near-black with a neon accent, or cream with terracotta. Those are common defaults.

### 6.3 Typography

| Role | Font | Notes |
|---|---|---|
| Headings, document titles | Source Serif 4 | Gives the "official record" feel |
| Interface text, tables | Public Sans | Clear at small sizes |
| Hindi and other Indic text | Noto Sans Devanagari and matching Noto families | Must render properly in every table and viewer |
| Numbers in tables | Public Sans with tabular figures on | Columns line up |

Rules:

- **Bundle fonts inside the app.** No Google Fonts or any web request.
- Scale: 12, 14, 16, 20, 26, 34 px. No sizes outside the scale.
- Body line length under 80 characters. Serif text gets slightly more line height than sans.
- Sentence case everywhere. No all-caps labels.
- Do not highlight one word in a heading with a different colour or italic.
- Do not put a small label above every heading. Add a label only when it carries information.

### 6.4 Layout and shape

- Layout follows the work: a permanent left rail for navigation, a wide centre for the document or table, a narrow right column for details.
- Left-align text and tables. Centre only the splash and login.
- Use **tables** for lists of applications, documents, and results. Do not chop everything into identical cards.
- Different things get different shapes. Panels use a 6 px radius, inputs 4 px, status stamps a squared 2 px edge with a thin double border. Do not apply one radius to everything.
- Borders and dividers must carry meaning (separating a group, marking a selected row). If a line is only decoration, remove it.
- Use numbering only for real sequences, such as the steps of a batch job.
- Keep spacing on an 4 px grid. Dense where people scan (tables), generous where people read (document viewer).

### 6.5 The dashboard

- Do not open with a row of big-number cards and a gradient chart. That is the default look.
- Lead with a **ledger**: one table showing documents processed, auto-verified, sent to review, and mismatches, with time per document beside each row.
- Below it, charts that answer a question: "Where do mismatches come from?" "Is accuracy improving?" "How many hours did we save?"
- Every chart has a plain-language title that states the finding, a labelled axis, and a way to click through to the underlying applications.
- Hours saved shows its formula on hover, so the number can be defended.

### 6.6 Words in the interface

- Write from the user's side. Say "Check a document", not "Run inference".
- Buttons say what happens: "Save correction", "Start batch", "Export report". Not "Submit".
- An action keeps its name everywhere: the button says "Start batch", the message says "Batch started".
- Errors explain the problem and the fix: "This scan is too blurry to read. Upload a sharper copy." Never "Something went wrong."
- Errors do not apologise. Empty screens invite action: "No applications yet. Import a biodata file to begin."
- No emoji. No exclamation marks. No marketing language.

### 6.7 Icons and imagery

- One icon set, one stroke weight. Icons support a label, they do not replace it in navigation.
- No stock illustrations, no robot or brain imagery, no "AI sparkle" symbols.
- The only large visual in the product is the document itself.

### 6.8 Motion

- Motion answers an action: a field turning from "Check" to "Match" after accept, a panel opening.
- No entrance animations on page load, no fade-and-slide on every section, no hover effects on every row.
- One allowed moment: when an instant check finishes, the field stamps land on the document in sequence (under 400 ms total). This is the demo highlight.
- Respect the operating system's reduced-motion setting.

### 6.9 Accessibility floor

- Every control reachable and visible by keyboard, with a clear focus ring.
- Review shortcuts: `A` accept, `E` edit, `R` reject, `N` next. Shown in a help panel.
- Works at 100% to 150% system scaling. Minimum window size 1280 x 720.
- Table rows, charts, and status marks have text equivalents for screen readers.

### 6.10 Design review checklist

Before any UI change is merged, answer these:

- [ ] Would this screen look the same in a different product for a different client? If yes, change it.
- [ ] Is every border, colour, and line carrying information?
- [ ] Is there only one place where the design is bold?
- [ ] Does it work for Hindi text, long names, and 5,000 rows?
- [ ] Are the error and empty states written, not left as defaults?

---

## 7. Git and teamwork rules

- Branches: `feature/<short-name>`, `fix/<short-name>`. Never commit straight to `main`.
- Commit messages: a short verb phrase: "Add QR decoding to degree marksheets".
- One pull request, one purpose. Under 400 changed lines where possible.
- A pull request needs one reviewer and green checks before merge.
- Do not commit: model weights (use Git LFS or the `models/` download script), real documents, `.env` files, build output.
- Version numbers follow `MAJOR.MINOR.PATCH`. Every release has a changelog entry.

---

## 8. Documentation rules

Keep these files current. A feature without docs is not done.

| File | Contents |
|---|---|
| `README.md` | What it is, how to install, how to run, in under 10 steps |
| `docs/architecture.md` | Diagram of the app, engine, and database, in simple terms |
| `docs/pipeline.md` | Each pipeline stage with input, output, and time budget |
| `docs/decisions.md` | Why each major library or approach was chosen |
| `docs/accuracy-report.md` | Latest accuracy and speed results with test set size |
| `DEMO.md` | The 3-minute demo script and sample files to use |

---

## 9. Presentation rules (for the final demo)

- Demo from the **installed** app on a clean machine, not from the editor.
- Keep sample files ready: one clean marksheet, one with an altered percentage, one Hindi certificate, one blurry scan, one batch of 200.
- Show the timer on the instant check. Under 3 seconds must be visible.
- Show a failure on purpose (blurry scan) and the clear message that follows. It proves the system handles reality.
- Show the accuracy table including the review rate. Be ready to explain how Three Sigma is measured.
- Have a one-page diagram of the pipeline ready: Preprocess, Classify, OCR, Extract, Verify, Review.
- Keep a recorded backup of the demo in case of hardware trouble.

---

## 10. When in doubt

1. Choose the simpler option.
2. Choose the option that can be explained in one sentence.
3. Choose the option that works offline.
4. Ask a teammate before inventing a new pattern.