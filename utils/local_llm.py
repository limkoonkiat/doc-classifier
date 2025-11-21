from utils.local_vectordb_helpers import local_load_knowledge_base
import os

import streamlit as st
from dotenv import load_dotenv
from langchain.chains import (create_history_aware_retriever,
                              create_retrieval_chain)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import (ChatPromptTemplate, MessagesPlaceholder,
                               PromptTemplate)
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_ollama.llms import OllamaLLM
import logging

# Set up logging to show in terminal
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.DEBUG)
logging.getLogger("langchain.chains").setLevel(logging.DEBUG)
logging.getLogger("langchain_ollama").setLevel(logging.DEBUG)

load_dotenv(override=True)


llm_model = OllamaLLM(model=os.getenv("LLM_MODEL"), base_url="http://localhost:11434", temperature=0.0)

vector_store_retriever = local_load_knowledge_base(
).as_retriever(search_kwargs={"k": 3}, temperature=0.0)


def get_qa_completion(retriever_system_prompt, query_system_prompt, user_input, chat_hist):

    # Contextualize question
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", retriever_system_prompt),
            MessagesPlaceholder("chat_hist"),
            ("user", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm_model, vector_store_retriever, contextualize_q_prompt
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", query_system_prompt),
            MessagesPlaceholder("chat_hist"),
            ("user", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm_model, qa_prompt)
    rag_chain = create_retrieval_chain(
        history_aware_retriever, question_answer_chain)
    response = rag_chain.invoke({"input": user_input, "chat_hist": chat_hist})
    return response


def get_classification_completion(retriever_system_prompt, query_system_prompt, user_input):
    multiquery_q_prompt = PromptTemplate.from_template(retriever_system_prompt)

    multiquery_retriever = MultiQueryRetriever.from_llm(
        vector_store_retriever, llm_model, multiquery_q_prompt)

    classify_prompt = PromptTemplate.from_template(query_system_prompt)

    classify_chain = create_stuff_documents_chain(
        llm_model, classify_prompt)
    rag_chain = create_retrieval_chain(
        multiquery_retriever, classify_chain)
    response = rag_chain.invoke({"input": user_input, "question": user_input})
    print("Response from RAG:\n")
    print(response)
    return response
