# Pysqlite3 required for Streamlit Cloud, comment out if not working on local
import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st

from cloak.cloak_utils import display_cloak_section
from logic.submit_handler import (get_classification_result, submit_text_input,
                                  submit_uploaded_file)
from utils.access import check_password
from utils.ui_helpers import create_custom_divider, set_stcode_style
from utils.vectordb_helpers import load_knowledge_base


if not check_password():
    st.stop()

set_stcode_style()

st.title("Data Classification Assistant")

with st.expander("IMPORTANT NOTICE"):
    st.write("""This web application is developed as a proof-of-concept prototype. The information provided here is NOT intended for actual usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.
    Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.
    Always consult with qualified professionals for accurate and personalized advice.""")

st.subheader("Enter your text or upload a file for classification")

tab1, tab2 = st.tabs(["Text Input", "File Upload"])

with tab1:

    with st.form("text_input_form"):
        st.subheader("Enter your text")
        if "saved_text_input" in st.session_state:
            st.session_state["text_input"] = st.session_state["saved_text_input"]
        st.text_area("", height=200, key="text_input")
        submitted = st.form_submit_button(
            "Submit", on_click=submit_text_input)

with tab2:
    with st.form("file_upload_form"):
        st.subheader("Upload your file")
        file_uploader_label = "Choose a file"
        allowed_file_types = ["txt", "docx"]

        st.file_uploader(file_uploader_label, type=allowed_file_types, accept_multiple_files=False, key="uploaded_file", help=None,
                         on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible", width="stretch")

        submitted = st.form_submit_button(
            "Submit", on_click=submit_uploaded_file)

if st.session_state.get("submitted"):
    st.divider()
    st.subheader("Classification Results")
    create_custom_divider("both")
    st.code(get_classification_result(), language=None)

    col1, col2 = st.columns(2, border=True)

    with col1:
        st.subheader("Security Classification Reasoning")
        create_custom_divider("security")
        st.code(st.session_state.get("security_classification", "N/A"),
                language=None, wrap_lines=True)
        st.code(st.session_state.get("security_reasoning", "N/A"),
                language=None, wrap_lines=True)

    with col2:
        st.subheader("Sensitivity Classification Reasoning")
        create_custom_divider("sensitivity")
        st.code(st.session_state.get("sensitivity_classification",
                "N/A"), language=None, wrap_lines=True)
        st.code(st.session_state.get("sensitivity_reasoning", "N/A"),
                language=None, wrap_lines=True)

    last_submitted_mode = st.session_state.get("submitted_mode")
    if last_submitted_mode == "text" or (last_submitted_mode == "file" and st.session_state.get("file_extension") == ".txt"):
        st.divider()
        st.subheader("Downgrade your classification")
        st.write("Potentially damaging parts of the text are highlighted in bold.")
        with st.container(border=True):
            st.markdown(st.session_state.get(
                "document_text", ""), unsafe_allow_html=True)

    st.divider()
    display_cloak_section()

load_knowledge_base()
