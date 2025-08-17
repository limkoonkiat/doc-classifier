from urllib import response
import streamlit as st

from logic.query_handler import generate_qna_response
from utils.access import check_password


if not check_password():
    st.stop()


st.title("Q&A Assistant")
st.write("Welcome to the Q&A Assistant! You can ask questions related to data classification, and I will do my best to assist you.")

default_greeting = {"role": "assistant",
                    "content": "Hello! Do you have any questions about data classification?"}

if "qna_messages" not in st.session_state:
    st.session_state.qna_messages = [default_greeting]

for message in st.session_state.qna_messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

user_input = st.chat_input("Type your question here...")

if user_input:
    st.session_state.qna_messages.append(
        {"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    response = generate_qna_response(user_input).get(
        "answer", "Sorry, there was an error processing your request.")
    st.session_state.qna_messages.append(
        {"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)


def clear_chat():
    st.session_state.qna_messages = [default_greeting]


st.button("Clear Chat", on_click=clear_chat)
