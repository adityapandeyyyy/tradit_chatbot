import streamlit as st
import pandas as pd
from google import genai
from google.genai import types

# -----------------------------
# Configuration & Caching
# -----------------------------
# We cache the data loading so the Excel isn't re-read on every rerun
@st.cache_data
def load_excel_data(path):
    df = pd.read_excel(path)
    # Convert rows to a clean string format for the AI
    return "\n".join([str(row.to_dict()) for _, row in df.iterrows()])

# -----------------------------
# Setup AI Client
# -----------------------------
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# Define the model and system-level rules
# Using System Instructions is much more reliable than putting rules in the prompt
SYSTEM_INSTRUCTION = """
You are a professional AI assistant. 
1. Answer questions ONLY using the provided Excel data.
2. If the answer is not in the data, say "I'm sorry, that information is not in the records."
3. Do NOT use outside knowledge or hallucinate.
"""

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="AI Data Assistant", layout="centered")
st.title("📊 BI Assistant")

# Load data
try:
    context_data = load_excel_data("ManpowerPython_BI.xlsx")
except FileNotFoundError:
    st.error("Excel file not found. Please check 'ManpowerPython_BI.xlsx'.")
    st.stop()

query = st.text_input("What would you like to know about the manpower data?", 
                     placeholder="e.g., How many employees are in Department X?")

if query:
    with st.spinner("Analyzing data..."):
        # The latest SDK uses client.models.generate_content
        response = client.models.generate_content(
            model="gemini-flash-latest",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.1,  # Lower temperature = more factual/less creative
            ),
            contents=[
                f"Data Context:\n{context_data}",
                f"User Question: {query}"
            ]
        )

    st.subheader("Answer")
    st.markdown(response.text)

# Footer info
st.divider()
st.caption(" For suggestions reach out to aditya.pandey4@jublfood.com")
