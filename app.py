import json
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

from prompt import SYSTEM_INSTRUCTION, build_user_prompt

SOURCE_LABELS = {
    "who_fruits_vegetables.txt": "World Health Organization (WHO)",
    "who_free_sugars.txt": "World Health Organization (WHO)",
    "who_ultra_processed_foods.txt": "World Health Organization (WHO)",
    "who_beverages_alcohol.txt": "World Health Organization (WHO)",
    "efsa_fiber.txt": "European Food Safety Authority (EFSA)",
    "mediterranean_diet.txt": "BMJ (British Medical Journal)",
}

# --------------------------------------------------
# Setup
# --------------------------------------------------

load_dotenv()
client = genai.Client()

st.set_page_config(
    page_title="Food Health Checker",
    page_icon="🥗",
)

st.title("🥗 Food Health Checker")
st.write(
    "This is a quick, judgment-free check-in on how healthy your diet is.\n\n"
    "Just write roughly what you ate — no need to be perfect. "
    "You’ll get a high-level score and one clear thing to focus on.\n\n"
    "_Not medical advice._"
)

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def render_list(items):
    if not items:
        st.write("- None")
        return
    for item in items:
        st.write(f"- {item}")

# --------------------------------------------------
# Input
# --------------------------------------------------

food_log = st.text_area(
    "What did you eat this week?",
    height=220,
    placeholder=(
        "Monday: bread with jam, banana, pasta carbonara, salad\n"
        "Tuesday: yogurt with granola, chicken sandwich, rice with vegetables\n"
        "7 coffees, 3 glasses of wine, 2 beers, 1 fruit smoothie"
    ),
)

st.markdown("")

analyze_clicked = st.button(
    "🥗 Check my diet",
    use_container_width=True
)

if analyze_clicked:
    st.info("⬇️ Your results are shown below. This may take a few seconds.")

# --------------------------------------------------
# Analysis
# --------------------------------------------------

if analyze_clicked:
    if not food_log.strip():
        st.warning("Please enter what you ate this week.")
    else:
        with st.spinner("Looking at patterns in your week…"):
            try:
                response = client.models.generate_content(
                    model="models/gemini-flash-latest",
                    contents=build_user_prompt(food_log),
                    config={
                        "system_instruction": SYSTEM_INSTRUCTION,
                        "temperature": 0.3,
                    },
                )
            except ClientError as e:
                if "RESOURCE_EXHAUSTED" in str(e):
                    st.warning(
                        "⏳ The app is temporarily busy. "
                        "Please wait about 30 seconds and try again."
                    )
                    st.stop()
                else:
                    raise

        try:
            data = json.loads(response.text)

            score = data.get("overall_score", 0)

            st.subheader("Overall health score")
            st.progress(score / 100)
            st.markdown(f"### **{score} / 100**")

            if score < 41:
                st.caption("Overall pattern needs improvement")
            elif score < 61:
                st.caption("Fair overall balance, but room to improve")
            elif score < 81:
                st.caption("Good overall balance")
            else:
                st.caption("Excellent overall balance")

            st.subheader("Summary")
            st.write(data.get("summary", ""))

            st.markdown("### ⭐ Focus for next week")
            st.info(data.get("recommendation", ""))

            st.caption("If you’re curious, you can dig a bit deeper 👇")

            with st.expander("See details: positives, concerns & nutrients"):
                st.subheader("✅ Positives")
                render_list(data.get("positives"))

                st.subheader("⚠️ Concerns")
                render_list(data.get("concerns"))

                st.subheader("🥦 Missing nutrients")
                render_list(data.get("missing_nutrients"))

            with st.expander("📚 Why this advice"):
                for src in data.get("sources", []):
                    label = SOURCE_LABELS.get(src.get("source_id"), src.get("source_id"))
                    st.markdown(f"**{label}**")
                    st.caption(src.get("reason", ""))
                    st.markdown("---")

        except json.JSONDecodeError:
            st.error("The model returned invalid JSON.")
            st.code(response.text)
        except Exception as e:
            st.error("Something went wrong while displaying the results.")
            st.exception(e)
            st.code(response.text)

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown("---")
st.caption(
    "_If you are reading this, thanks for testing my LLM + RAG experiment._"
)
