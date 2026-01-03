# Food Health Checker — Grounded Nutrition Feedback with RAG

A lightweight web app that analyzes weekly eating habits and provides **source-grounded, non-judgmental nutrition feedback**, powered by Gemini and Retrieval-Augmented Generation (RAG).

**Live app:**  
https://healthyfood-chatbot-carlo.streamlit.app

---

## What this app does

This app lets users describe what they ate over the past week and returns:

- An overall diet quality score (0–100)
- A short, human-readable summary
- One clear recommendation to focus on next week
- Supporting positives, concerns, and missing nutrients
- Transparent references to authoritative sources (WHO, EFSA, BMJ)

**Important:**  
This is **not medical advice**. The app is designed for learning and reflection only.

---

## Why this project exists

Large Language Models are powerful, but **unreliable without grounding** — especially for domains like nutrition where hallucinations are risky.

This project was built to understand and implement:

- Retrieval-Augmented Generation (RAG)
- Semantic search with embeddings
- Vector similarity search
- Source attribution and guardrails
- Practical deployment of an LLM-powered app

Rather than a prompt-only demo, the app **forces the model to reason strictly over retrieved guideline content**.

---

## High-level architecture

User input (food log)
↓
Gemini embedding model
↓
FAISS vector similarity search
↓
Relevant guideline chunks
↓
Grounded prompt to Gemini
↓
Structured JSON response
↓
Streamlit UI + source explanations

---

## How RAG works in this app

This app uses **Retrieval-Augmented Generation (RAG)** to ensure all advice is grounded in official nutrition guidelines rather than the model’s general knowledge.

### 1. Knowledge ingestion
- Nutrition guidelines are stored as plain `.txt` files in the `knowledge/` folder
- Each file represents an authoritative source (e.g. WHO, EFSA, BMJ)
- Each file is treated as a **knowledge chunk**

### 2. Embedding the knowledge
- Each knowledge chunk is converted into a vector using:
  - `models/text-embedding-004` (Gemini)
- These vectors capture **semantic meaning**, not just keywords

### 3. Building the vector index
- All embeddings are stored in a local **FAISS** index
- FAISS enables fast similarity search without any external services
- This keeps the system:
  - Lightweight
  - Easy to reason about
  - Cheap to run

### 4. Semantic retrieval
- The user’s food log is also embedded
- FAISS retrieves the **most semantically similar** guideline chunks
- This solves issues like:
  - “banana” → “fruit”
  - “wine” → “alcohol”
  - “fiber” → “whole grains”

### 5. Grounded generation
- Only retrieved chunks are injected into the prompt
- The LLM is instructed to:
  - Use **only the provided sources**
  - Return **valid JSON only**
  - Include a structured `sources` field
  - Avoid unsupported claims or hallucinations

### 6. Transparent output
- The UI displays:
  - One clear recommendation
  - Supporting positives and concerns
  - Which authoritative sources were used, and why

---

## Key design decisions

### Why embeddings instead of keyword search?

Keyword matching breaks quickly with real user input:
- Different wording
- Synonyms
- Vague descriptions

---

### Why FAISS?

- No managed service required
- Full control over retrieval logic
- Easy to debug and reason about
- Perfect for small–medium knowledge bases

FAISS can later be swapped for a managed vector database if needed.

---

## Sources used

- World Health Organization (WHO)
- European Food Safety Authority (EFSA)
- BMJ (British Medical Journal)

The model is explicitly instructed **not to invent sources** and to reference only retrieved content.

---

## Limitations (by design)

- FAISS index is rebuilt per request (acceptable at this scale)
- No user history or personalization
- No medical personalization (intentionally avoided)

---

## Possible next steps

- Persist and cache the FAISS index
- Automatically ingest and chunk PDFs
- Add hybrid retrieval (BM25 + embeddings)
- Add evaluation to verify correct source usage
- Introduce user feedback loops
- Swap FAISS for a managed vector database if scaling
- Support user uploading a photo of food to use as prompt
- Support user recording voice to describe what user ate that week (instead of typing)

---