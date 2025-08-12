import os

import streamlit as st
from dotenv import load_dotenv
from langchain.chains import (RetrievalQA, create_history_aware_retriever,
                              create_retrieval_chain)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import (ChatPromptTemplate, MessagesPlaceholder,
                               PromptTemplate)
from langchain_openai import ChatOpenAI
from openai import OpenAI

from utils.vectordb_helpers import load_knowledge_base

if load_dotenv('.env'):
    # for local development
    OPENAI_KEY = os.getenv('OPENAI_API_KEY')
else:
    OPENAI_KEY = st.secrets.get('OPENAI_API_KEY')

# Pass the API key to the OpenAI client
client = OpenAI(api_key=OPENAI_KEY)

llm = ChatOpenAI(model="gpt-4o-mini")

vector_store_retriever = load_knowledge_base(
).as_retriever(search_kwargs={"k": 5})


def get_embedding(input, model='text-embedding-3-small'):
    response = client.embeddings.create(
        input=input,
        model=model
    )
    return [x.embedding for x in response.data]


def get_qa_completion_with_chat_hist(template, chat_hist, user_input):
    # Contextualize question
    contextualize_q_system_prompt = """
    You are a assistant helping to retrieve relevant documents about data classification from a vector database. 
    Given a chat history and the latest user question which might reference context in the chat history, \
    formulate a standalone question which can be understood without the chat history.
    The reformulated question must be useful enough to retrieve relevant context from the vector database.
    Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_hist"),
            ("user", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, vector_store_retriever, contextualize_q_prompt
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", template),
            MessagesPlaceholder("chat_hist"),
            ("user", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(
        history_aware_retriever, question_answer_chain)
    response = rag_chain.invoke({"input": user_input, "chat_hist": chat_hist})
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
    print(len(response["source_documents"]))
    for i in range(len(response["source_documents"])):
        doc = response["source_documents"][i]
        print(f"Content {i+1}: {doc.page_content}")

    return response


def get_completion(prompt, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1, json_output=False):
    # This is the "Updated" helper function for calling LLM
    if json_output == True:
        output_json_structure = {"type": "json_object"}
    else:
        output_json_structure = None

    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(  # originally was openai.chat.completions
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=n,
        response_format=output_json_structure,
    )
    return response.choices[0].message.content


def get_completion_by_messages(messages, model="gpt-4o-mini", temperature=0.2, top_p=0.6, max_tokens=1024, n=1):
    # Note that this function directly take in "messages" as the parameter.
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=n
    )
    return response.choices[0].message.content
