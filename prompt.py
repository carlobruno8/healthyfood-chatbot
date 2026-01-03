import os
import numpy as np
import faiss
from google import genai

def embed_texts(texts: list[str], client) -> np.ndarray:
    """
    Convert a list of texts into embedding vectors using Gemini.
    """
    response = client.models.embed_content(
        model="models/text-embedding-004",
        contents=texts
    )

    embeddings = [e.values for e in response.embeddings]

    return np.array(embeddings, dtype="float32")


def load_knowledge_chunks():
    chunks = []

    for root, _, files in os.walk("knowledge"):
        for file in files:
            if file.endswith(".txt"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    chunks.append({
                        "id": file,
                        "content": f.read()
                    })
    return chunks

def build_knowledge_index(chunks: list, client):
    """
    Build a FAISS index from knowledge chunks.
    """
    texts = [chunk["content"] for chunk in chunks]

    embeddings = embed_texts(texts, client)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index

SYSTEM_INSTRUCTION = """
You are a nutrition analysis assistant.

Rules:
- Base advice on WHO and EFSA dietary guidelines
- Do NOT provide medical advice
- Assume a healthy adult with no allergies
- Be practical, supportive, and concise
- Do not moralize food choices
- Keep information short and clear
- If a claim is not supported by the provided guidelines, do not include it

When referencing sources inline in text fields, use human-readable authority names:
- (World Health Organization – WHO)
- (European Food Safety Authority – EFSA)
- (BMJ – British Medical Journal)

Do NOT include file names, source IDs, URLs, or technical identifiers
inside text fields.

Include a structured "sources" field listing only sources that were actually used.
Do not invent sources.

Scoring guidelines:
- 0–40: Poor
- 41–60: Fair
- 61–80: Good
- 81–100: Excellent

Output rules:
- Return VALID JSON ONLY
- Do not include markdown
- Do not include explanations outside JSON
"""


def build_user_prompt(food_log: str, client) -> str:
    # 1. Load all knowledge chunks
    all_chunks = load_knowledge_chunks()

    # 2. Build embeddings + FAISS index
    index = build_knowledge_index(all_chunks, client)

    # 3. Retrieve semantically relevant chunks
    relevant_chunks = retrieve_relevant_chunks(
        query=food_log,
        chunks=all_chunks,
        index=index,
        client=client,
        top_k=4
    )

    # 4. Assemble knowledge text
    knowledge_text = ""
    for chunk in relevant_chunks:
        knowledge_text += f"\n[Source ID: {chunk['id']}]\n{chunk['content']}\n"

    # 5. Return the final prompt
    return f"""
You are given the following nutrition knowledge.
Each source has an ID.

{knowledge_text}

Here is what I ate this week:

{food_log}

Analyze the diet USING ONLY the information from the sources above
and return a JSON object with EXACTLY these keys:
- "overall_score": number between 0 and 100
- "summary": string
- "positives": array of strings
- "concerns": array of strings
- "missing_nutrients": array of strings
- "recommendation": string
- "sources": array of objects, each with:
    - "source_id": string
    - "reason": string
"""

def retrieve_relevant_chunks(
    query: str,
    chunks: list,
    index,
    client,
    top_k: int = 4
):
    # 1. Embed the user query
    query_embedding = embed_texts([query], client)

    # 2. Search the FAISS index
    scores, indices = index.search(query_embedding, top_k)

    # 3. Return the matched chunks
    results = []
    for idx in indices[0]:
        if idx < len(chunks):
            results.append(chunks[idx])

    return results