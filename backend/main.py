from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
import json

# ---------- APP ----------
app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- VECTOR DB ----------
DB_PATH = "../vectorstore"

embeddings = HuggingFaceEmbeddings()

db = FAISS.load_local(
    DB_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

# ---------- OPENAI ----------
client = OpenAI()

# ---------- REQUEST MODEL ----------
class Query(BaseModel):
    question: str


# ---------- MAIN ENDPOINT ----------
@app.post("/ask")
def ask_question(query: Query):

    query_text = f"Find purchase order details: {query.question}"

    docs = db.similarity_search(query_text, k=10)

    if not docs:
        return {
            "results": [],
            "insight": "No relevant data found.",
            "analytics": ""
        }

    combined_text = "\n\n".join([doc.page_content for doc in docs])

    # ---------- STRUCTURED DATA ----------
    structured_prompt = f"""
Extract structured purchase order data.

Return ONLY valid JSON array.
No explanations.

Fields (if available):
- po_number
- vendor
- date
- amount
- reason

Context:
{combined_text}
"""

    structured_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": structured_prompt}]
    )

    raw_output = structured_response.choices[0].message.content

    try:
        structured_data = json.loads(raw_output)
        if not isinstance(structured_data, list):
            structured_data = []
    except:
        structured_data = [{
            "error": "Parsing failed",
            "raw_output": raw_output[:300]
        }]

    # ---------- INSIGHT ----------
    insight_prompt = f"""
User Question: {query.question}

Explain the result in 2-3 simple lines.
Keep it short and clear.
"""

    insight_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": insight_prompt}]
    )

    insight_text = insight_response.choices[0].message.content.strip()

    # ---------- ANALYTICS ----------
    analytics_prompt = f"""
Find patterns or trends from this data:

{combined_text}

Rules:
- Max 2 lines
- Only if meaningful
- Else return empty
"""

    analytics_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": analytics_prompt}]
    )

    analytics_text = analytics_response.choices[0].message.content.strip()

    return {
        "results": structured_data,
        "insight": insight_text,
        "analytics": analytics_text
    }


# ---------- SUGGESTIONS ----------
@app.get("/suggestions")
def get_suggestions():
    return {
        "suggestions": [
            "List all vendors",
            "Show PO numbers",
            "Extract dates",
            "Highest spend vendor"
        ]
    }