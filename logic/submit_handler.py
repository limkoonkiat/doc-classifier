import json
import tempfile

import streamlit as st
from langchain_community.document_loaders import Docx2txtLoader, TextLoader

from logic import query_handler


def submit_text_input(text_input):
    if not text_input:
        st.error("Please enter some text before submitting.")
        return

    response = query_handler.generate_rag_response(text_input)
    save_result(response)


def submit_uploaded_file(uploaded_file):
    if uploaded_file is None:
        st.error("Please upload a file before submitting.")
        return

    file_extension = uploaded_file.name.split('.')[-1].lower()

    if file_extension not in ['txt', 'docx']:
        st.error("Unsupported file format. Please upload a supported file.")
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    if file_extension == 'txt':
        loader = TextLoader(temp_path, encoding='utf-8')
    elif file_extension == 'docx':
        loader = Docx2txtLoader(temp_path)
    else:
        return None

    documents = loader.load()

    full_text = "".join([doc.page_content for doc in documents])

    response = query_handler.generate_rag_response(full_text)
    save_result(response)


def save_result(response):
    print(response)
    print(response["result"])
    json_string = extract_curly_only(response["result"])
    json_output = json.loads(json_string)
    st.session_state['security_classification'] = json_output.get(
        'security_classification', '')
    st.session_state['sensitivity_classification'] = json_output.get(
        'sensitivity_classification', '')
    st.session_state['security_reasoning'] = json_output.get(
        'security_reasoning', '')
    st.session_state['sensitivity_reasoning'] = json_output.get(
        'sensitivity_reasoning', '')
    st.session_state['document_text'] = json_output.get('document_text', '')


def extract_curly_only(text):
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and start < end:
        return text[start:end + 1]
    else:
        return text


def get_classification_result():
    if 'security_classification' not in st.session_state or st.session_state['security_classification'] == "":
        return "N/A"
    elif 'sensitivity_classification' not in st.session_state or st.session_state['sensitivity_classification'] == "":
        return "N/A"
    else:
        return "{} / {}".format(st.session_state['security_classification'], st.session_state['sensitivity_classification'])
