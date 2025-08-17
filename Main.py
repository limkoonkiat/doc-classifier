import sys

import streamlit as st

from cloak_utils.cloak import cloak_it
from logic import submit_handler
from utils.access import check_password
from utils.vectordb_helpers import load_knowledge_base

# Pysqlite3 required for Streamlit Cloud, comment out if not working on local
__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")


if not check_password():
    st.stop()


st.title("Data Classification Assistant")

with st.expander("IMPORTANT NOTICE"):
    st.write("""This web application is developed as a proof-of-concept prototype. The information provided here is NOT intended for actual usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.
    Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.
    Always consult with qualified professionals for accurate and personalized advice.""")

st.subheader("Enter your text or upload a file for classification")

tab1, tab2 = st.tabs(["Text Input", "File Upload"])

with tab1:

    with st.form("text_input_form"):
        st.header("Enter your text below.")
        if "saved_text_input" in st.session_state:
            st.session_state["text_input"] = st.session_state["saved_text_input"]
        st.text_area("Enter your text here:", height=200, key="text_input")
        submitted = st.form_submit_button(
            "Submit", on_click=submit_handler.submit_text_input)

with tab2:
    with st.form("file_upload_form"):
        st.header("Upload your file below.")
        file_uploader_label = "Choose a file"
        allowed_file_types = ["txt", "docx"]

        st.file_uploader(file_uploader_label, type=allowed_file_types, accept_multiple_files=False, key="uploaded_file", help=None,
                         on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible", width="stretch")

        submitted = st.form_submit_button(
            "Submit", on_click=submit_handler.submit_uploaded_file)

if st.session_state.get("submitted"):
    st.subheader("Classification Results")
    st.code(submit_handler.get_classification_result(), language=None)

    col1, col2 = st.columns(2, border=True)

    with col1:
        st.subheader("Security Classification Reasoning")
        st.code(st.session_state.get("security_classification", "N/A"),
                language=None, wrap_lines=True)
        st.code(st.session_state.get("security_reasoning", "N/A"),
                language=None, wrap_lines=True)

    with col2:
        st.subheader("Sensitivity Classification Reasoning")
        st.code(st.session_state.get("sensitivity_classification",
                "N/A"), language=None, wrap_lines=True)
        st.code(st.session_state.get("sensitivity_reasoning", "N/A"),
                language=None, wrap_lines=True)

    last_submitted_mode = st.session_state.get("submitted_mode")
    if last_submitted_mode == "text" or (last_submitted_mode == "file" and st.session_state.get("file_extension") == ".txt"):
        st.subheader("Downgrade your classification")
        st.write("Potentially damaging parts of the text are highlighted in bold.")
        with st.container(border=True):
            st.markdown(st.session_state.get("document_text", ""), unsafe_allow_html=True)

        st.subheader("Cloak It!")
        st.write("You can use Govtech's Cloak to mask specific Personally Identifiable Information (PII) in the text to potentially lower the security and/or sensitivity classifications.")
        st.button("Cloak my text!", key="pressed_cloak")

        with st.container():
            if st.session_state.get("pressed_cloak"):
                with st.container(border=True):
                    cloak_text = cloak_it(st.session_state.get("text_input", ""))
                    st.write(submit_handler.clean_text_for_markdown(cloak_text))

load_knowledge_base()
