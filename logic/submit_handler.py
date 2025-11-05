import json
import os
import tempfile
import streamlit as st
from langchain_community.document_loaders import Docx2txtLoader

from logic import query_handler


def submit_text_input():
    if not st.session_state["text_input"]:
        st.error("Please enter some text before submitting.")
        return

    response = query_handler.generate_rag_response(
        st.session_state["text_input"])
    save_result(response)
    st.session_state["submitted"] = True
    st.session_state["submitted_mode"] = "text"
    st.session_state["saved_text_input"] = st.session_state["text_input"]


def submit_uploaded_file():
    if not st.session_state.get("uploaded_file"):
        st.error("Please upload a file before submitting.")
        return

    uploaded_file = st.session_state["uploaded_file"]
    file_extension = os.path.splitext(uploaded_file.name)[1]
    st.session_state["file_extension"] = file_extension

    if file_extension not in [".txt", ".docx"]:
        st.error("Unsupported file format. Please upload a supported file.")
        return

    temp_file = tempfile.NamedTemporaryFile(
        delete=False, suffix=file_extension)
    temp_file.write(uploaded_file.read())  # write bytes
    temp_file.close()
    temp_path = temp_file.name

    try:
        if file_extension == ".txt":
            with open(temp_path, "r", encoding="UTF-8") as f:
                full_text = f.read()
            st.session_state["saved_text_input"] = full_text
        elif file_extension == ".docx":
            loader = Docx2txtLoader(temp_path)
        elif file_extension == ".pdf":
            pass
            # loader = PdfLoader(temp_path)
        else:
            st.error("Unsupported file type")
            st.stop()
    except Exception as e:
        st.error(f"Error loading file: {e}")
        os.remove(temp_path)
        return

    if file_extension != ".txt":
        documents = loader.load()
        full_text = "".join([doc.page_content for doc in documents])

    os.remove(temp_path)

    response = query_handler.generate_rag_response(full_text)
    save_result(response)
    st.session_state["submitted"] = True
    st.session_state["submitted_mode"] = "file"


def save_result(response):
    json_string = extract_curly_only(response["answer"])
    json_output = json.loads(json_string)
    st.session_state["security_classification"] = json_output.get(
        "security_classification", "")
    st.session_state["sensitivity_classification"] = json_output.get(
        "sensitivity_classification", "")
    st.session_state["security_reasoning"] = json_output.get(
        "security_reasoning", "")
    st.session_state["sensitivity_reasoning"] = json_output.get(
        "sensitivity_reasoning", "")
    st.session_state["document_text"] = clean_text_for_markdown(json_output.get(
        "document_text", ""))


def extract_curly_only(text):
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and start < end:
        return text[start:end + 1]
    else:
        return text


def clean_text_for_markdown(text):
    text = text.replace("$", "\\$")
    return text


def get_classification_result():
    if "security_classification" not in st.session_state or st.session_state["security_classification"] == "":
        return "N/A"
    elif "sensitivity_classification" not in st.session_state or st.session_state["sensitivity_classification"] == "":
        return "N/A"
    else:
        return "{} / {}".format(st.session_state["security_classification"], st.session_state["sensitivity_classification"])
