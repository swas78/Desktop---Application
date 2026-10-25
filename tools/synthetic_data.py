# For: Generating realistic synthetic test documents and batch verification samples
# Must never: Use or leak real personally identifiable information

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)


def create_clean_marksheet_pdf(path: Path) -> dict:
    """Generates a clean degree marksheet PDF with matching data."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 720, "XYZ INSTITUTE OF TECHNOLOGY - PROVISIONAL CERTIFICATE")
    c.setFont("Helvetica", 11)
    c.drawString(100, 680, "Candidate Name: Rahul Kumar Sharma")
    c.drawString(100, 650, "Father's Name: Mohan Sharma")
    c.drawString(100, 620, "Date of Birth: 14/05/1999")
    c.drawString(100, 590, "Roll Number: EC21S12345")
    c.drawString(100, 560, "Degree: Bachelor of Technology (ECE)")
    c.drawString(100, 530, "Aggregate Percentage: 74.20%")
    c.drawString(100, 500, "Result: FIRST CLASS WITH DISTINCTION")
    c.drawString(100, 450, "advs_qr:{\"name\":\"Rahul Kumar Sharma\",\"percentage\":\"74.20\",\"roll_no\":\"EC21S12345\"}")
    c.save()
    return {
        "fullName": "Rahul Kumar Sharma",
        "fatherName": "Mohan Sharma",
        "dob": "1999-05-14",
        "qualification": {"percentage": 74.20, "branch": "ECE", "degree": "BTech"}
    }


def create_altered_marksheet_pdf(path: Path) -> dict:
    """Generates marksheet with discrepancy: form says 74.2, document has 72.4."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 720, "STATE TECHNICAL UNIVERSITY - GRADE CARD")
    c.setFont("Helvetica", 11)
    c.drawString(100, 680, "Candidate Name: Rahul Kumar Sharma")
    c.drawString(100, 650, "Father's Name: Mohan Sharma")
    c.drawString(100, 620, "Date of Birth: 14/05/1999")
    c.drawString(100, 590, "Roll Number: EC21S12345")
    c.drawString(100, 560, "Degree: Bachelor of Technology (ECE)")
    c.drawString(100, 530, "Aggregate Percentage: 72.40%")
    c.drawString(100, 500, "Result: FIRST CLASS")
    c.drawString(100, 450, "advs_qr:{\"name\":\"Rahul Kumar Sharma\",\"percentage\":\"72.40\",\"roll_no\":\"EC21S12345\"}")
    c.save()
    return {
        "fullName": "Rahul Kumar Sharma",
        "fatherName": "Mohan Sharma",
        "dob": "1999-05-14",
        "qualification": {"percentage": 74.20, "branch": "ECE", "degree": "BTech"}
    }


def create_blurry_scan_image(path: Path) -> dict:
    """Generates an excessively blurred image to test quality gate rejection."""
    img = Image.new("RGB", (800, 1100), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    draw.text((100, 100), "Unreadable scan document sample", fill=(100, 100, 100))
    # Heavy Gaussian blur to drop sharpness below threshold
    blurred = img.filter(ImageFilter.GaussianBlur(radius=14))
    blurred.save(str(path))
    return {"fullName": "Test Applicant"}


def generate_all_samples():
    """Generates complete suite of demo sample documents."""
    clean_path = SAMPLE_DIR / "sample_clean_marksheet.pdf"
    clean_bio = create_clean_marksheet_pdf(clean_path)
    (SAMPLE_DIR / "sample_clean_biodata.json").write_text(json.dumps(clean_bio, indent=2))

    altered_path = SAMPLE_DIR / "sample_altered_marksheet.pdf"
    alt_bio = create_altered_marksheet_pdf(altered_path)
    (SAMPLE_DIR / "sample_altered_biodata.json").write_text(json.dumps(alt_bio, indent=2))

    blurry_path = SAMPLE_DIR / "sample_blurry_scan.png"
    create_blurry_scan_image(blurry_path)
    print(f"Generated samples in {SAMPLE_DIR}")


if __name__ == "__main__":
    generate_all_samples()
