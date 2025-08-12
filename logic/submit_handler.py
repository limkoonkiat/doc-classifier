import json
import tempfile

import streamlit as st
from langchain_community.document_loaders import Docx2txtLoader, TextLoader

from logic import query_handler


def submit_text_input():
    if 'text_input' in st.session_state:
        text_input = st.session_state['text_input']
        print("text input")

        if not text_input:
            st.error("Please enter some text before submitting.")
            return

        # Process the input text
        response = query_handler.generate_rag_response(
            st.session_state['text_input'])
        print(len(response.get("source_documents")))
        save_result(response)


def submit_uploaded_file():
    return
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
        temp_file.write(uploaded_file.getvalue())
        print(temp_file)
        location = temp_file.name

    file_type = uploaded_file.type
    try:
        if file_type == 'text/plain':
            loader = TextLoader(location)
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            loader = Docx2txtLoader(location)
        else:
            return None

        document = loader.load()
        return document

    except Exception as e:
        raise ValueError(
            "Unsupported file format. Please upload a .docx file.") from e


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
