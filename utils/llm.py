import os

import streamlit as st
import tiktoken
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from openai import OpenAI

if load_dotenv('.env'):
    # for local development
    OPENAI_KEY = os.getenv('OPENAI_API_KEY')
else:
    OPENAI_KEY = st.secrets.get('OPENAI_API_KEY')

# Pass the API key to the OpenAI client
client = OpenAI(api_key=OPENAI_KEY)


def get_embedding(input, model='text-embedding-3-small'):
    response = client.embeddings.create(
        input=input,
        model=model
    )
    return [x.embedding for x in response.data]


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


def get_rag_completion(user_input, template, vector_store):
    qa_chain_prompt = PromptTemplate.from_template(
        template)

    qa_chain = RetrievalQA.from_chain_type(
        ChatOpenAI(model='gpt-4o-mini'),
        # chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": qa_chain_prompt}
    )
    response = qa_chain.invoke({"query": user_input})
    return response


def count_tokens(text):
    # This function is for calculating the tokens given the "message"
    # This is simplified implementation that is good enough for a rough estimation
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    return len(encoding.encode(text))


def count_tokens_from_messages(messages):
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    value = ' '.join([x.get('content') for x in messages])
    return len(encoding.encode(value))
