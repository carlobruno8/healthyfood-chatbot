import os

def load_knowledge_chunks():
    chunks = []

    for root, _, files in os.walk("knowledge"):
        for file in files:
            if file.endswith(".txt"):
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    chunks.append({
                        "id": file,
                        "content": f.read()
                    })
    return chunks


def select_relevant_chunks(food_log: str, chunks: list, max_chunks: int = 4):
    food_log_lower = food_log.lower()
    scored_chunks = []

    for chunk in chunks:
        score = sum(
            1 for word in food_log_lower.split()
            if word in chunk["content"].lower()
        )
        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(reverse=True, key=lambda x: x[0])

    return [chunk for _, chunk in scored_chunks[:max_chunks]]

SYSTEM_INSTRUCTION = """
You are a nutrition analysis assistant.

Rules:
- Base advice on WHO and EFSA dietary guidelines
- Do NOT provide medical advice
- Assume a healthy adult with no allergies
- Be practical, supportive, and concise
- Do not moralize food choices
- Keep it short and clean in terms of information
- Feel free to quote sources specified, but only the if listed in the guidelines 
- If a claim is not supported by the provided guidelines, do not include it
- Make sure the result for key recommendation only has one, clear recommendation

When referencing sources inline in text fields, use human-readable
authority names, for example:
- (World Health Organization - WHO)
- (European Food Safety Authority - EFSA)

Do NOT include file names, source IDs, URLs, or technical identifiers
inside text fields.

Source IDs may only be used internally and in the "sources" field if requested.

Scoring guidelines:
- 0–40: Poor
- 41–60: Fair
- 61–80: Good
- 81–100: Excellent

Output rules:
- Return VALID JSON ONLY
- Do not include markdown
- Do not include explanations outside JSON

In addition to inline authority labels (e.g. WHO, EFSA, BMJ),
include a structured "sources" field.

Only include sources that were actually used.
Each source must reference one of the source IDs provided.
Do not invent sources.

"""

def build_user_prompt(food_log: str) -> str:
    all_chunks = load_knowledge_chunks()
    relevant_chunks = select_relevant_chunks(food_log, all_chunks)

    knowledge_text = ""
    for chunk in relevant_chunks:
        knowledge_text += f"\n[Source ID: {chunk['id']}]\n{chunk['content']}\n"

    return f"""
You are given the following nutrition knowledge.
Each source has an ID.

Source label mapping:
- who_fruits_vegetables.txt → WHO
- who_free_sugars.txt → WHO
- efsa_fiber.txt → EFSA
- mediterranean_diet.txt → BMJ

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
