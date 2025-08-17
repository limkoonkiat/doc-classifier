import streamlit as st

from utils.access import check_password


if not check_password():
    st.stop()


st.title("Sample Inputs")

st.write("This page provides sample inputs for testing the application.")

st.write("Note that we only have simple mock emails for now.")

for i in range(1, 11):
    with open(f"data/letter_{i}.txt", "r", encoding="utf-8") as file:
        letter_content = file.read()
    st.subheader(f"Sample Email {i}")
    st.code(letter_content, language="text", wrap_lines=True)
