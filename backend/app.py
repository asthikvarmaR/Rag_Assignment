import sys
from pdf_loader import load_pdfs
from embeddings import chunk_text, embed_texts
from vector_store import (
    create_collection,
    store_embeddings,
    search,
    file_already_uploaded
)
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def upload_documents():
    print("📄 Scanning data folder...")
    docs = load_pdfs()

    for doc in docs:
        file_name = doc["file"]

        if file_already_uploaded(file_name):
            print(f"⏭️ Skipping (already uploaded): {file_name}")
            continue

        print(f"⬆️ Uploading: {file_name}")

        chunks = chunk_text(doc["text"])
        embeddings = embed_texts(chunks)

        store_embeddings(chunks, embeddings, file_name)

    print("✅ Upload complete!")


def query_mode():
    while True:
        q = input("\nAsk something (or 'exit'): ")
        if q.lower() == "exit":
            break

        query_vector = model.encode(q).tolist()
        results = search(query_vector)

        print("\n🔍 Results:")
        for res in results:
            print(f"[{res.payload['file']}] - {res.payload['text'][:200]}")


if __name__ == "__main__":
    if "--upload" in sys.argv:
        upload_documents()
    else:
        query_mode()