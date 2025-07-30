import streamlit as st
import pandas as pd
from logic.query_handler import process_user_message

st.title('Main Page')

form = st.form(key='form')
form.subheader("Prompt")

mock_data = {
    "DocumentID": [1, 2, 3, 4, 5],
    "Title": ["Doc A", "Doc B", "Doc C", "Doc D", "Doc E"],
    "Category": ["Finance", "HR", "Tech", "Marketing", "Legal"],
    "Score": [87, 92, 76, 81, 95]
}

df = pd.DataFrame(mock_data)
st.write(df)


user_prompt = form.text_area("Enter your prompt here:", height=200)

if form.form_submit_button("Submit"):
    st.toast(f"User Input Submitted - {user_prompt}")
    response = process_user_message(user_prompt)
    st.write(response)
