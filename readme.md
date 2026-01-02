# Food Health Checker

A small experimental app that uses a Large Language Model (Gemini) to analyze a
weekly food log and provide a health score and practical dietary feedback.

This project is built as a **learning exercise** to explore:
- Prompt design
- Retrieval-Augmented Generation (RAG)
- LLM-backed applications
- Lightweight deployment workflows

---

## sequence

1. You enter a free-text description of what you ate during the week.
2. The app evaluates the input against high-level nutrition guidelines.
3. It returns:
   - An overall health score (0–100)
   - A short summary
   - Positives
   - Concerns
   - Missing nutrients
   - Practical food-based recommendations

The app assumes a healthy adult with no allergies and does **not** provide medical advice.

---

## RAG

The analysis is grounded using a small, explicit knowledge base based on:
- World Health Organization (WHO) dietary guidance
- European Food Safety Authority (EFSA) principles

This is implemented via prompt-based RAG for clarity and transparency.

---

## stack

- Python
- Streamlit
- Google Gemini API
- Prompt-based RAG (no vector database)

---

## run locally
pip install -r requirements.txt
streamlit run app.py

---

## disclaimer
This project is for educational and experimental purposes only. It does not provide medical or personalized dietary advice.