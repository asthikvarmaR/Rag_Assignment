def load_pdfs():
    documents = []

    for file in os.listdir(DATA_PATH):
        if file.endswith(".pdf"):
            path = os.path.join(DATA_PATH, file)
            reader = PdfReader(path)

            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""

            documents.append({
                "file": file,
                "text": text
            })

    return documents