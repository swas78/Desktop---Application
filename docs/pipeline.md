<!-- For: Document verification pipeline specification and stage budget breakdown -->
<!-- Must never: Omit input/output contracts or time budgets for any processing stage -->

# Document Processing Pipeline

The ADVS verification engine runs a 9-stage intelligent document processing pipeline designed to complete within a strict 3.0-second latency budget per single-page document.

| Stage | Input | Output | Time Budget | Implementation Module |
|---|---|---|---|---|
| **1. Ingest & Quality Gate** | Raw document bytes | Decoded page images & quality score | 0.20 s | `engine/app/pipeline/ingest.py` |
| **2. Preprocess** | Decoded page images | Contrast-stretched, deskewed images | 0.30 s | `engine/app/pipeline/preprocess.py` |
| **3. OCR & Bounding Boxes** | Document file & images | Text runs, spatial bounding boxes, word confidence | 0.80 s | `engine/app/pipeline/ocr.py` |
| **4. Classify** | Images + OCR snippet | Document type & classification confidence | 0.20 s | `engine/app/pipeline/classify.py` |
| **5. QR & Barcode Decode** | Images & text metadata | Structured QR payload if present | 0.10 s | `engine/app/pipeline/qr_decode.py` |
| **6. Language & Translate** | Extracted text | Detected language (en/hi) & side-by-side mapping | 0.30 s | `engine/app/pipeline/translate.py` |
| **7. Field Extraction** | Text boxes & QR payloads | Typed fields with bounding boxes & confidence | 0.50 s | `engine/app/pipeline/extract.py` |
| **8. Verification** | Extracted fields + biodata | Per-field status, Three Sigma auto-accept, alert list | 0.10 s | `engine/app/pipeline/verify.py` |
| **9. Authenticity Heuristics** | Document metadata & images | Authenticity risk score (0.0 to 1.0) & warning flags | 0.10 s | `engine/app/pipeline/authenticity.py` |
| **Total** | | | **~2.6 s (Budget &le; 3.0 s)** | `engine/app/pipeline/manager.py` |

---

## Confidence and Quality Gate Policy
- **Quality Gate**: Evaluates Laplacian high-frequency edge energy and resolution. Blurry scans below the 0.35 threshold abort early with the message: *"This scan is too blurry to read. Upload a sharper copy."*
- **Three Sigma Auto-Accept**: When extracted field confidence is &ge; 0.97 and status is `match`, the field is auto-accepted. Any discrepancy or lower confidence routes the document to the manual human review queue.
