import os
import streamlit as st
import pandas as pd

from logic.submit_handler import get_elapsed_processing_time, submit_text_input

st.title("Sample Inputs")

st.write("This page provides sample inputs for testing the application.")

st.write("Note that we only have simple mock emails for now.")

def test_samples():
    if "all_sample_results" not in st.session_state:
        st.session_state["all_sample_results"] = pd.DataFrame([{"time": "", "security": "", "sensitivity": "", "security_reasoning": "", "sensitivity_reasoning": ""} for i in range(10)])
    for i in range(1, 11):
        if st.session_state.get(f"run_sample_test_{i}"):
            with open(f"data/letter_{i}.txt", "r", encoding="utf-8") as file:
                letter_content = file.read()
                st.session_state["text_input"] = letter_content
                submit_text_input()
            time = get_elapsed_processing_time()
            security = st.session_state.get("security_classification", "N/A")
            security_reasoning = st.session_state.get("security_reasoning", "N/A")
            sensitivity_reasoning = st.session_state.get("sensitivity_reasoning", "N/A")
            sensitivity = st.session_state.get("sensitivity_classification", "N/A")
            result = {"time": time, "security": security, "sensitivity": sensitivity, "security_reasoning": security_reasoning, "sensitivity_reasoning": sensitivity_reasoning}
            st.session_state["all_sample_results"].loc[i-1] = result
    st.session_state["text_input"] = ""

with st.popover("Select Samples"):
    col1, col2, col3, col4, col5 = st.columns(5, gap="small", border=True)
    col6, col7, col8, col9, col10 = st.columns(5, gap="small", border=True)

cols = [col1, col2, col3, col4, col5, col6, col7, col8, col9, col10]

for i in range(1, 11):
    with cols[i-1]:
        st.checkbox(f"Test Sample {i}", value=True, key=f"run_sample_test_{i}")

st.button("Test samples", on_click=test_samples)
st.markdown(f":blue-badge[{os.getenv('LLM_MODEL')}] :green-badge[{os.getenv('EMBEDDING_MODEL')}]")

if "all_sample_results" in st.session_state:
    df = pd.DataFrame(st.session_state["all_sample_results"])
    df.index = pd.RangeIndex(start=1, stop=len(df) + 1, step=1)
    st.write(df)

for i in range(1, 11):
    with open(f"data/letter_{i}.txt", "r", encoding="utf-8") as file:
        letter_content = file.read()
    st.subheader(f"Sample Email {i}")
    st.code(letter_content, language="text", wrap_lines=True)



