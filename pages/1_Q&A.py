import streamlit as st
from logic.query_handler import process_user_message


st.title("Q&A Bot")

form = st.form(key='form')
form.subheader("Prompt")

user_prompt = form.text_area("Enter your prompt here:", height=200)

if form.form_submit_button("Submit"):
    st.toast(f"User Input Submitted - {user_prompt}")
    response = process_user_message(user_prompt)
    st.write(response)
