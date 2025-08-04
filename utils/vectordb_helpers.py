import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from utils.llm import count_tokens

text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=500,
    chunk_overlap=50,
    length_function=count_tokens
)


@st.cache_resource
def load_knowledge_base(file_path='data/Data Classification Guide.docx'):

    loader = UnstructuredWordDocumentLoader(
        file_path, mode='elements', strategy='fast')
    documents = loader.load()

    splitted_documents = text_splitter.split_documents(documents)

    preprocess_for_embedding(splitted_documents)

    # for testing
    print_documents_to_file(splitted_documents)

    try:
        vector_store = Chroma.from_documents(
            documents=splitted_documents,
            embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        )
        return vector_store
    except Exception as e:
        st.error(f"Error creating vector store: {e}")
        return None


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


def print_documents_to_file(documents, output_file='data/documents.txt'):
    # This function prints the documents to a file for debugging purposes.
    # Clear and then write to output file to see chunks
    with open('data/documents.txt', 'w', encoding='utf-8') as f:
        f.truncate(0)  # Clear the file

    for doc in documents:
        with open('data/documents.txt', 'a', encoding='utf-8') as f:
            f.write("Chunk: ")
            f.write(str(doc))
            f.write('\n\n')
