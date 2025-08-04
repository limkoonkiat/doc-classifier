import sys

import streamlit as st

from logic import submit_handler
from utils import vectordb_helpers

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")


st.title('Data Classification Assistant')

st.subheader("Enter your text or upload a file for classification")

tab1, tab2 = st.tabs(["Text Input", "File Upload"])

with tab1:
    with st.form("text_input_form"):
        st.header("Enter your text below.")
        st.text_area("Enter your text here:", height=200, key="text_input")
        submitted = st.form_submit_button(
            "Submit", on_click=submit_handler.submit_text_input)

with tab2:
    with st.form("file_upload_form"):
        st.header("Upload your file below.")
        file_uploader_label = "Choose a file"
        allowed_file_types = ["txt", "docx"]

        uploaded_file = st.file_uploader(file_uploader_label, type=allowed_file_types, accept_multiple_files=False, key=None, help=None,
                                         on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible", width="stretch")

        # if uploaded_file is not None:
        # st.write(f"File '{uploaded_file.name}' uploaded successfully.")
        # doc = file_helpers.process_uploaded_file(uploaded_file)

        submitted = st.form_submit_button(
            "Submit", on_click=submit_handler.submit_uploaded_file)

if submitted:
    st.toast("Form submitted!")

st.subheader("Classification Results")
st.code(submit_handler.get_classification_result(), language=None)

col1, col2 = st.columns(2, border=True)

with col1:
    st.subheader("Security Classification Reasoning")
    st.code(st.session_state.get("security_reasoning", "N/A"),
            language=None, wrap_lines=True)

with col2:
    st.subheader("Sensitivity Classification Reasoning")
    st.code(st.session_state.get("sensitivity_reasoning", "N/A"),
            language=None, wrap_lines=True)

st.subheader("Downgrade your classification")
with st.container(border=True):
    st.write(st.session_state.get("document_text", "N/A"))

vector_db = vectordb_helpers.load_knowledge_base()
