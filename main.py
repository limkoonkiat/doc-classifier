import pandas as pd
import streamlit as st
from docx import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader


from logic.query_handler import process_user_message

st.title('Main Page')

form = st.form(key='form')
form.subheader("Prompt")


user_prompt = form.text_area("Enter your prompt here:", height=200)

if form.form_submit_button("Submit"):
    st.toast(f"User Input Submitted - {user_prompt}")
    response = process_user_message(user_prompt)
    st.write(response)

text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],
    chunk_size=500,
    chunk_overlap=50
)

doc = TextLoader('data/testing.txt').load()

docs = text_splitter.split_documents(doc)

vector_store = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
)
