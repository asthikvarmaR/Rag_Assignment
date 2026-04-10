import re

def extract_po_details(text):
    text = text.replace("\n", " ")

    patterns = {
        "PO Number": r"(PO\s*(Ref\s*)?No[:\s]*[A-Z0-9\/\-]+)",
        "Date": r"(Date[:\s]*\d{2}[-/]\d{2}[-/]\d{4})",
        "Vendor": r"([A-Z][A-Za-z\s&]+(Pvt\. Ltd\.|Ltd\.|LLP))",
        "Phone": r"(\+91[\s\-]?\d{10})",
        "Amount": r"(₹?\s?\d{1,3}(,\d{3})*(\.\d{2})?)"
    }

    extracted = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        extracted[key] = match.group(0) if match else "Not found"

    return extracted


def build_structured_results(results):
    seen_files = {}
    final = []

    for res in results:
        payload = res.payload or {}

        file_name = payload.get("file", "Unknown File")
        text = payload.get("text", "").strip()

        if not text:
            continue

        if file_name not in seen_files:
            seen_files[file_name] = extract_po_details(text)

    for file_name, data in seen_files.items():
        row = {"File": file_name}
        row.update(data)
        final.append(row)

    return final