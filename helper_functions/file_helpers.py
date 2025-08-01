import tempfile
import lolviz
import streamlit as st
from langchain_community.document_loaders import Docx2txtLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from helper_functions.llm import count_tokens


def load_knowledge_base(file_path='data/Data Classification Guide.docx'):
    loader = UnstructuredWordDocumentLoader(
        file_path, mode='elements', strategy='fast')
    # loader = Docx2txtLoader(location)
    document = loader.load()

    splitted_document = text_splitter.split_documents(document)

    st.write(lolviz.objviz(splitted_document))

    for i, chunk in enumerate(splitted_document):
        st.write(f"Chunk {i + 1}:")
        st.write(chunk.page_content)
        st.write("---")


def process_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
        temp_file.write(uploaded_file.getvalue())
        print(temp_file)
        location = temp_file.name

    file_type = uploaded_file.type
    print(file_type)
    print(location)
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


text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=500,
    chunk_overlap=50,
    length_function=count_tokens
)
