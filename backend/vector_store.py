from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    VectorParams,
    Distance
)

from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME, VECTOR_SIZE
import uuid

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# =========================
# CREATE COLLECTION
# =========================
def create_collection_if_not_exists():
    try:
        collections = client.get_collections().collections
        existing = [c.name for c in collections]

        if COLLECTION_NAME not in existing:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )

            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name="file",
                field_schema="keyword"
            )

    except Exception as e:
        print("Collection error:", e)


# =========================
# STORE EMBEDDINGS (FIXED)
# =========================
def store_embeddings(texts, embeddings, file_name):
    create_collection_if_not_exists()

    points = []

    for i in range(len(texts)):
        text = texts[i].strip()

        if not text:
            continue

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embeddings[i].tolist(),
                payload={
                    "text": text,
                    "file": file_name
                }
            )
        )

    # 🚨 Prevent empty upload crash
    if not points:
        print(f"⚠️ No valid data to store for {file_name}")
        return

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )


# =========================
# SEARCH (MODERN API)
# =========================
def search(query_vector):
    create_collection_if_not_exists()

    try:
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=3
        )
        return results.points

    except Exception as e:
        print("Search error:", e)
        return []


# =========================
# DUPLICATE CHECK
# =========================
def file_already_uploaded(file_name):
    create_collection_if_not_exists()

    try:
        result = client.count(
            collection_name=COLLECTION_NAME,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="file",
                        match=MatchValue(value=file_name)
                    )
                ]
            )
        )
        return result.count > 0

    except Exception as e:
        print("Duplicate check error:", e)
        return False