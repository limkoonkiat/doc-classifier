import zipfile
from io import StringIO

import pandas as pd
import streamlit as st
import tiktoken
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from lxml import etree


def count_tokens(text):
    # This function is for calculating the tokens given the "message"
    # This is simplified implementation that is good enough for a rough estimation
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    return len(encoding.encode(text))


def count_tokens_from_messages(messages):
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    value = ' '.join([x.get('content') for x in messages])
    return len(encoding.encode(value))


text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=500,
    chunk_overlap=50,
    length_function=count_tokens
)


@st.cache_resource(show_spinner=True)
def load_knowledge_base(file_path='data/Data Classification Guide.docx'):

    loader = UnstructuredWordDocumentLoader(
        file_path, mode='elements', strategy='fast')
    documents = loader.load()

    documents.extend(extract_footnotes(file_path))

    splitted_documents = text_splitter.split_documents(documents)

    processed_documents = process_for_embedding(splitted_documents)

    # for testing
    print_documents_to_file(processed_documents)

    try:
        vector_store = Chroma.from_documents(
            documents=processed_documents,
            embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        )
        return vector_store
    except Exception as e:
        st.error(f"Error creating vector store: {e}")
        return None


def extract_footnotes(file_path):
    with zipfile.ZipFile(file_path, 'r') as docx_zip:
        if "word/footnotes.xml" not in docx_zip.namelist():
            return []

        footnotes_xml = docx_zip.read('word/footnotes.xml')
        tree = etree.fromstring(footnotes_xml)

        footnotes = []

        for footnote in tree.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}footnote'):
            footnote_text = ''.join(footnote.itertext()).strip()
            if footnote_text:
                footnote_doc = Document(footnote_text)
                footnote_doc.metadata = {
                    'source': file_path,
                    'file_directory': 'data',
                    'filename': file_path.split('/')[-1],
                    'category': 'References',
                    'section': 'References'
                }
                footnotes.append(footnote_doc)
    return footnotes


def process_for_embedding(documents):
    # TODO raptor retrievalaugmentation?
    processed_documents = []
    current_section = ''
    for doc in documents:
        clean_metadata(doc)
        if doc.metadata.get("category") == "Table":
            # Assuming that the table title is always the previous element,
            # merge the title with the table content
            table_title_doc = processed_documents.pop()
            process_table(table_title_doc, doc)

        # Find and add the titles of the section we are currently in to metadata
        elif doc.metadata.get("category") == "Title":
            current_section = doc.page_content.strip()

        doc.metadata["section"] = current_section
        processed_documents.append(doc)

    return processed_documents


def clean_metadata(doc):
    if not isinstance(doc.metadata, dict):
        doc.metadata = {}
    for key, value in doc.metadata.items():
        if isinstance(value, (str, int, float, bool, type(None))):
            continue
        elif isinstance(value, list):
            doc.metadata[key] = str(value[0])
        else:
            doc.metadata[key] = str(value)


def process_table(table_title_doc, table_content_doc):
    # TODO Write a summary of the table?

    # Extract table title from previous document
    table_title = table_title_doc.page_content

    # In table content document, extract text_as_html (already in html format) from metadata
    table_content = StringIO(table_content_doc.metadata.get("text_as_html"))
    # Remove text_as_html metadata from table_content_doc
    if "text_as_html" in table_content_doc.metadata:
        del table_content_doc.metadata["text_as_html"]

    # Convert to markdown
    markdown_table = (pd.read_html(table_content, header=0)[0].to_markdown())

    # Merge table title and table content into page_content of table content document
    table_content_doc.page_content = f"[{table_title}]\n" + \
        markdown_table + "\n"


def print_documents_to_file(documents, output_file='data/documents.txt'):
    # This function prints the documents to a file for debugging purposes.
    # Clear and then write to output file to see chunks
    with open(output_file, 'w', encoding='utf-8') as f:
        f.truncate(0)  # Clear the file

    for i in range(len(documents)):
        doc = documents[i]
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"Chunk {i+1}: \n")
            f.write(f"Page Content: {doc.page_content}\n")
            f.write(f"Metadata: {doc.metadata}\n")
            f.write('\n\n')
