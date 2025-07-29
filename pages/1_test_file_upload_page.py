import streamlit as st

st.title('File Upload')

file_uploader_label = "Choose a file"
allowed_file_types = ["txt"]

st.file_uploader(file_uploader_label, type=allowed_file_types, accept_multiple_files=False, key=None, help=None,
                 on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible", width="stretch")

