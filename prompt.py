def load_knowledge() -> str:
    with open("knowledge/nutrition_guidelines.txt", "r") as f:
        return f.read()

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
    knowledge = load_knowledge()

    return f"""
You are given the following nutrition guidelines:

{knowledge}

Here is what I ate this week:

{food_log}

Analyze the diet USING ONLY the information from the nutrition guidelines above
and return a JSON object with EXACTLY these keys:
- "overall_score": number between 0 and 100
- "summary": string
- "positives": array of strings
- "concerns": array of strings
- "missing_nutrients": array of strings
- "recommendations": array of strings
"""
