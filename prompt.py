import os

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
- who_fruits_vegetables.txt → World Health Organization (WHO)
- who_free_sugars.txt → World Health Organization (WHO)
- who_ultra_processed_foods.txt → World Health Organization (WHO)
- who_beverages_alcohol.txt → World Health Organization (WHO)
- efsa_fiber.txt → European Food Safety Authority (EFSA)
- mediterranean_diet.txt → BMJ (British Medical Journal)

{knowledge_text}

Here is what I ate this week:

{food_log}

Analyze the diet USING ONLY the information from the sources above
and return a JSON object with EXACTLY these keys:
- "overall_score": number between 0 and 100
- "summary": string
- "positives": array of strings (or empty array)
- "concerns": array of strings (or empty array)
- "missing_nutrients": array of strings (or empty array)
- "recommendation": string
- "sources": array of objects, each with:
    - "source_id": string
    - "reason": string
"""
