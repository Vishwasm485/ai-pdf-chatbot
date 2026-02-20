import fitz
import re
import os

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)      # remove extra spaces/newlines
    text = re.sub(r'-\s+', '', text)      # fix broken hyphen words
    return text.strip()

def load_pdf(file_path):

    # ---- SAFETY CHECKS ----
    if not os.path.exists(file_path):
        raise ValueError(f"PDF not found: {file_path}")

    if os.path.getsize(file_path) == 0:
        raise ValueError("Uploaded PDF is empty. Please upload again.")

    # ---- OPEN PDF ----
    doc = fitz.open(file_path)

    docs = []
    for page_num, page in enumerate(doc):
        raw = page.get_text()
        cleaned = clean_text(raw)

        if cleaned:
            docs.append({
                "text": cleaned,
                "page": page_num + 1
            })

    if not docs:
        raise ValueError("No readable text found in PDF.")

    return docs