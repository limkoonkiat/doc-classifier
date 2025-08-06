import zipfile
from io import StringIO

from langchain_core.documents import Document
import pandas as pd
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from lxml import etree

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

    documents.extend(extract_footnotes(file_path))

    print("Loaded Documents:")  # Debugging line
    print(documents)

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
                    'category_depth': 0,
                    'file_directory': 'data',
                    'filename': file_path.split('/')[-1],
                    'filetype': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'category': 'Footnote',
                    'element_id': footnote.get('id', '')
                }
                footnotes.append(footnote_doc)
    return footnotes


# [Document(metadata={'source': 'data/Data Classification Guide.docx',
# 'category_depth': 0, 'file_directory': 'data', 'filename': 'Data Classification Guide.doc
# x', 'last_modified': '2025-08-04T16:33:53', 'page_number': 1, 'languages': ['eng'],
# 'filetype': 'application/vnd.openxmlformats-officedocument.wordprocessingm
# l.document', 'category': 'Title', 'element_id': '48078f80a5f7e13610c0b73985e47205'},
# page_content='Data Classification Guide'),

    print("Extracted Footnotes:")  # Debugging line
    print(footnotes)
    return footnotes


def process_for_embedding(documents):
    processed_documents = []
    for doc in documents:
        clean_metadata(doc)
        if doc.metadata.get("category") == "Table":
            # Assuming that the table title is always the previous element,
            # merge the title with the table content
            table_title_doc = processed_documents.pop()
            process_table(table_title_doc, doc)
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
    # Extract table title from previous document
    table_title = table_title_doc.page_content

    # In table content document, extract text_as_html (already in html format) from metadata
    table_content = StringIO(table_content_doc.metadata.get("text_as_html"))
    # Convert to markdown
    markdown_table = (pd.read_html(table_content, header=0)[0].to_markdown())

    # Merge table title and table content into page_content of table content document
    table_content_doc.page_content = f"[{table_title} - MARKDOWN FORMAT]\n" + \
        markdown_table + "\n"


def print_documents_to_file(documents, output_file='data/documents.txt'):
    # This function prints the documents to a file for debugging purposes.
    # Clear and then write to output file to see chunks
    with open(output_file, 'w', encoding='utf-8') as f:
        f.truncate(0)  # Clear the file

    for doc in documents:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write("Chunk: ")
            f.write(str(doc))
            f.write('\n\n')
