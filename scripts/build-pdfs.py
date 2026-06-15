#!/usr/bin/env python3
"""Rebuild Help Kit topic PDFs and the combined print pack.

Run from the repository root:

    python3 scripts/build-pdfs.py

The script includes known topic directories that exist locally, in the site's
preferred print-pack order. Add a new entry below when adding a new topic.
"""
from pathlib import Path
from sys import exit

from pypdf import PdfReader, PdfWriter
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
TOPICS = [
    ("heat", "heat-onepager.pdf"),
    ("smoke", "smoke-onepager.pdf"),
    ("naloxone", "naloxone-onepager.pdf"),
    ("ors", "ors-onepager.pdf"),
    ("choking", "choking-onepager.pdf"),
    ("bleeding", "bleeding-onepager.pdf"),
    ("cpr", "cpr-onepager.pdf"),
    ("stroke", "stroke-onepager.pdf"),
    ("burns", "burns-onepager.pdf"),
    ("triage", "triage-onepager.pdf"),
]

rendered = []
missing_indexes = []
for directory, pdf_name in TOPICS:
    html_path = ROOT / directory / "index.html"
    pdf_path = ROOT / directory / pdf_name
    if not html_path.exists():
        continue
    print(f"Rendering {html_path.relative_to(ROOT)} -> {pdf_path.relative_to(ROOT)}")
    HTML(filename=str(html_path)).write_pdf(str(pdf_path), presentational_hints=True)
    rendered.append(pdf_path)

if not rendered:
    exit("No topic index.html files found; run from a valid Help Kit checkout.")

writer = PdfWriter()
expected_pages = 0
for pdf_path in rendered:
    pages = len(PdfReader(str(pdf_path)).pages)
    expected_pages += pages
    print(f"Appending {pdf_path.relative_to(ROOT)} ({pages} pages)")
    writer.append(str(pdf_path))

pack_path = ROOT / "help-kit-print-pack.pdf"
with pack_path.open("wb") as fh:
    writer.write(fh)
actual_pages = len(PdfReader(str(pack_path)).pages)
print(f"Wrote {pack_path.relative_to(ROOT)} ({actual_pages} pages from {len(rendered)} topic PDFs)")
if actual_pages != expected_pages:
    exit(f"Print pack page count mismatch: expected {expected_pages}, got {actual_pages}")
