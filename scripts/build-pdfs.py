#!/usr/bin/env python3
"""Rebuild Help Kit topic PDFs and the combined print pack.

Run from the repository root:

    python3 scripts/build-pdfs.py

The pack opens with a one-page booklet cover/index (print-cover.html ->
print-cover.pdf), followed by the topic one-pagers in the site's preferred
print-pack order. Add a new entry to TOPICS below when adding a new topic.
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
    ("seizure", "seizure-onepager.pdf"),
    ("allergy", "allergy-onepager.pdf"),
    ("cold", "cold-onepager.pdf"),
    ("triage", "triage-onepager.pdf"),
]

# Render the booklet cover first so it leads the print pack.
cover_html = ROOT / "print-cover.html"
cover_pdf = ROOT / "print-cover.pdf"
rendered = []
if cover_html.exists():
    print(f"Rendering {cover_html.relative_to(ROOT)} -> {cover_pdf.relative_to(ROOT)}")
    HTML(filename=str(cover_html)).write_pdf(str(cover_pdf), presentational_hints=True)
    rendered.append(cover_pdf)

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
print(f"Wrote {pack_path.relative_to(ROOT)} ({actual_pages} pages from {len(rendered)} PDFs)")
if actual_pages != expected_pages:
    exit(f"Print pack page count mismatch: expected {expected_pages}, got {actual_pages}")
