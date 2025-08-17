from utils.vectordb_helpers import load_knowledge_base
import os

import streamlit as st
from dotenv import load_dotenv
from langchain.chains import (RetrievalQA, create_history_aware_retriever,
                              create_retrieval_chain)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import (ChatPromptTemplate, MessagesPlaceholder,
                               PromptTemplate)
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI
from openai import OpenAI
import logging
logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)


if load_dotenv(".env"):
    # for local development
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
else:
    OPENAI_KEY = st.secrets.get("OPENAI_API_KEY")

# Pass the API key to the OpenAI client
client = OpenAI(api_key=OPENAI_KEY)

llm = ChatOpenAI(model="gpt-4o-mini")

vector_store_retriever = load_knowledge_base(
).as_retriever(search_kwargs={"k": 5})


def get_embedding(input, model="text-embedding-3-small"):
    response = client.embeddings.create(
        input=input,
        model=model
    )
    return [x.embedding for x in response.data]


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
        llm, vector_store_retriever, contextualize_q_prompt
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", query_system_prompt),
            MessagesPlaceholder("chat_hist"),
            ("user", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(
        history_aware_retriever, question_answer_chain)
    response = rag_chain.invoke({"input": user_input, "chat_hist": chat_hist})
    return response


def get_classification_completion(retriever_system_prompt, query_system_prompt, user_input):
    multiquery_q_prompt = PromptTemplate.from_template(retriever_system_prompt)

    multiquery_retriever = MultiQueryRetriever.from_llm(
        vector_store_retriever, llm, multiquery_q_prompt)

    classify_prompt = PromptTemplate.from_template(query_system_prompt)

    classify_chain = create_stuff_documents_chain(
        llm, classify_prompt)
    rag_chain = create_retrieval_chain(
        multiquery_retriever, classify_chain)
    response = rag_chain.invoke({"input": user_input, "question": user_input})
    print("Response from RAG:\n")
    print(response)
    return response


def get_qa_completion(template, user_input):
    qa_chain_prompt = PromptTemplate.from_template(
        template)

    # TODO Multiquery retrival???
    # TODO reranking retrieval?

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store_retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": qa_chain_prompt}
    )
    response = qa_chain.invoke({"query": user_input})

    print("Response from RAG:\n")
    for i in range(len(response["source_documents"])):
        doc = response["source_documents"][i]
        print(f"Content {i+1}: {doc.page_content}")

    return response
