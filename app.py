import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai

from prompt import SYSTEM_INSTRUCTION, build_user_prompt

# --------------------------------------------------
# Setup
# --------------------------------------------------

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(
    page_title="Food Health Checker",
    page_icon="🥗",
)

st.title("🥗 Food Health Checker")
st.write(
    "This is a quick, judgment-free check-in on how healthy your diet is.\n\n"
    "Just write roughly what you ate — no need to be perfect. "
    "You’ll get a high-level score and a few practical suggestions.\n\n"
    "_Not medical advice. Just perspective._"
)

# --------------------------------------------------
# Helper for nice list rendering
# --------------------------------------------------

def render_list(items):
    for item in items:
        st.write(f"- {item}")

# --------------------------------------------------
# Text input
# --------------------------------------------------

food_log = st.text_area(
    "What did you eat this week?",
    height=220,
    placeholder=(
        "Monday: bread with jam, banana, pasta carbonara, salad\n"
        "Tuesday: yogurt with granola, chicken sandwich, rice with vegetables"
    ),
)

# --------------------------------------------------
# Analyze
# --------------------------------------------------

if st.button("Check my diet 🥗"):
    if not food_log.strip():
        st.warning("Please enter what you ate this week.")
    else:
        with st.spinner("Analyzing your diet…"):
            response = client.models.generate_content(
                model="models/gemini-flash-latest",
                contents=build_user_prompt(food_log),
                config={
                    "system_instruction": SYSTEM_INSTRUCTION,
                    "temperature": 0.3,
                },
            )

        try:
            data = json.loads(response.text)

            score = data["overall_score"]

            st.subheader("Overall health score")
            st.progress(score / 100)
            st.write(f"**{score} / 100**")

            if score < 41:
             st.caption("Overall pattern needs improvement")
            elif score < 61:
                st.caption("Fair overall balance, but room to improve")
            elif score < 81:
                st.caption("Good overall balance")
            else:
                st.caption("Excellent overall balance")

            st.subheader("Summary")
            st.write(data["summary"])


            st.subheader("⭐ Top 3 things to focus on next week")

            top_recs = data["recommendations"][:3]
            for rec in top_recs:
                st.write(f"- {rec}")


            st.subheader("More detailed analysis")

            with st.expander("See details: positives, concerns & nutrients"):
                st.subheader("✅ Positives")
                render_list(data["positives"])

                st.subheader("⚠️ Concerns")
                render_list(data["concerns"])

                st.subheader("🥦 Missing nutrients")
                render_list(data["missing_nutrients"])

            st.subheader("🍎 Recommendations")
            render_list(data["recommendations"])

        except Exception:
            st.error("The model returned an unexpected format.")
            st.text(response.text)

st.markdown("")
st.markdown("")
st.markdown("---")
st.caption(

    "_If you are reading this, thanks for testing my LLM + RAG experiment._"
)