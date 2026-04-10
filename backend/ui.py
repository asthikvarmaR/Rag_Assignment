import streamlit as st
import tempfile
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import pandas as pd

from embeddings import chunk_text, embed_texts
from vector_store import store_embeddings, search, file_already_uploaded
from extractor import build_structured_results

st.set_page_config(
    page_title="PO Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

model = SentenceTransformer("all-MiniLM-L6-v2")

# =========================
# SIDEBAR UPLOAD
# =========================
st.sidebar.title("📤 Upload Documents")

uploaded_files = st.sidebar.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if st.sidebar.button("Upload to Qdrant"):
    if not uploaded_files:
        st.sidebar.warning("Upload files first")
    else:
        for file in uploaded_files:
            file_name = file.name

            if file_already_uploaded(file_name):
                st.sidebar.info(f"Skipping: {file_name}")
                continue

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(file.read())
                temp_path = tmp.name

            reader = PdfReader(temp_path)

            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""

            chunks = chunk_text(text)
            chunks = [c.strip() for c in chunks if c.strip()]

            if not chunks:
                st.sidebar.warning(f"⚠️ No readable text: {file_name}")
                continue

            embeddings = embed_texts(chunks)

            store_embeddings(chunks, embeddings, file_name)

            st.sidebar.success(f"Uploaded: {file_name}")

        st.sidebar.success("✅ Upload complete")

# =========================
# MAIN UI
# =========================
st.title("📊 Purchase Order Intelligence Dashboard")
st.caption("Structured AI extraction from documents")

query = st.text_input(
    "🔍 Enter your query",
    placeholder="e.g. show PO details, vendor info, etc..."
)

if st.button("Submit"):
    if not query:
        st.warning("Enter a question")
    else:
        query_vector = model.encode(query).tolist()
        results = search(query_vector)

        if not results:
            st.info("No results found")
        else:
            structured_data = build_structured_results(results)

            if not structured_data:
                st.warning("No structured data extracted")
            else:
                df = pd.DataFrame(structured_data)

                st.subheader("📋 Extracted PO Data")
                st.dataframe(df, use_container_width=True)

                # =========================
                # OPTIONAL: RAW CONTEXT
                # =========================
                with st.expander("📄 Raw Context"):
                    for res in results:
                        payload = res.payload or {}

                        file_name = payload.get("file", "Unknown")
                        text = payload.get("text", "")

                        st.markdown(f"### 📁 {file_name}")
                        st.write(text[:300])
                        st.divider()