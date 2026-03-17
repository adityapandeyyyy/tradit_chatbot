import streamlit as st
import pandas as pd
from google import genai
from google.genai import types

# -----------------------------  
# Configuration & Caching
# -----------------------------
@st.cache_data
def load_excel_data(path):
    df = pd.read_excel(path)
    # Convert rows to a clean string format for the AI
    return "\n".join([str(row.to_dict()) for _, row in df.iterrows()])

# -----------------------------
# Setup AI Client
# -----------------------------
# Ensure GEMINI_API_KEY is set in your .streamlit/secrets.toml
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

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
        # API Call
        response = client.models.generate_content(
            model="gemini-3-flash-latest",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.1,  # Keep it factual
            ),
            contents=[
                f"Data Context:\n{context_data}",
                f"User Question: {query}"
            ]
        )

    # Display the AI Answer
    st.subheader("Answer")
    st.markdown(response.text)

    # --- TOKEN USAGE SECTION ---
    st.divider()
    st.subheader("Metadata & Usage")
    
    # Access usage_metadata from the response object
    usage = response.usage_metadata
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Input Tokens", usage.prompt_token_count)
    with col2:
        st.metric("Output Tokens", usage.candidates_token_count)
    with col3:
        st.metric("Total Tokens", usage.total_token_count)
    
    # Optional: Progress bar showing how much of the context window is used
    # Gemini 3 Flash has a 1M token context window
    usage_pct = (usage.total_token_count / 1000000) * 100
    st.progress(usage_pct / 100, text=f"Context Window Usage: {usage_pct:.4f}%")

# Footer info
st.divider()
st.caption("For suggestions reach out to aditya.pandey4@jublfood.com")
