import streamlit as st

from utils.file_helpers import (load_knowledge_base,
                                process_uploaded_file)

st.title('Classify your File')

st.write("Upload your file for classification.")

load_knowledge_base()

file_uploader_label = "Choose a file"
allowed_file_types = ["txt", "docx"]

uploaded_file = st.file_uploader(file_uploader_label, type=allowed_file_types, accept_multiple_files=False, key=None, help=None,
                                 on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible", width="stretch")

if uploaded_file is not None:
    st.write(f"File '{uploaded_file.name}' uploaded successfully.")
    doc = process_uploaded_file(uploaded_file)
