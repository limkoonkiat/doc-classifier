import tempfile
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import lolviz
import streamlit as st
from langchain_community.document_loaders import Docx2txtLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.llm import count_tokens
from langchain.schema import Document


@st.cache_resource
def load_knowledge_base(file_path='data/Data Classification Guide.docx'):

    loader = UnstructuredWordDocumentLoader(
        file_path, mode='elements', strategy='fast')
    documents = loader.load()

    splitted_documents = text_splitter.split_documents(documents)

    preprocess_for_embedding(splitted_documents)

    try:
        vector_store = Chroma.from_documents(
            documents=[testing("aaa", {"source": "test"}, id="1")],
            embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        )
        return vector_store
    except Exception as e:
        st.error(f"Error creating vector store: {e}")
        return None


def process_uploaded_file(uploaded_file):
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


def preprocess_for_embedding(documents):
    for doc in documents:
        doc.metadata = clean_metadata(doc.metadata)


def clean_metadata(metadata):
    if not isinstance(metadata, dict):
        return {}
    new_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool, type(None))):
            new_metadata[key] = value
        elif isinstance(value, list):
            new_metadata[key] = str(value[0])
        else:
            new_metadata[key] = str(value)
    return new_metadata


text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=500,
    chunk_overlap=50,
    length_function=count_tokens
)


class testing:
    def __init__(self, page_content, metadata=None, id=None):
        self.page_content = page_content
        self.metadata = metadata or {}
        self.id = id
