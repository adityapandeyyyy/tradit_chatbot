import streamlit as st
import pandas as pd
import google.generativeai as genai

# -----------------------------
# Load Excel
# -----------------------------
file_path = r"C:\Users\aditya.pandey4\Downloads\ManpowerPython_BI.xlsx"

df = pd.read_excel(file_path)

documents = []

for _, row in df.iterrows():
    documents.append(str(row.to_dict()))

# -----------------------------
# Load Secret Key
# -----------------------------
api_key = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("AI Assistant")

query = st.text_input("Ask AI")

if query:
    context = "\n".join(documents)

    prompt = f"""
You are an AI assistant. Do NOT hallucinate.

Answer ONLY from the Excel data below.

Context:
{context}

Question:
{query}
"""

    response = model.generate_content(prompt)

    st.write("Answer")
    st.write(response.text)
