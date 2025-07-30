import streamlit as st
import pandas as pd
from logic.query_handler import process_user_message
from docx import Document


st.title('Main Page')

form = st.form(key='form')
form.subheader("Prompt")

# Load the document
doc = Document('data/cases.docx')

# Extract the table
table = doc.tables[0]  # Assuming you want the first table

# Create a list to hold the data
data = []

# Iterate through the rows in the table
for row in table.rows:
    data.append([cell.text for cell in row.cells])

# Create a DataFrame
columns = data[0]  # Assuming the first row is the header
mock_data = pd.DataFrame(data[1:], columns=columns)

df = pd.DataFrame(mock_data)
st.write(df)


user_prompt = form.text_area("Enter your prompt here:", height=200)

if form.form_submit_button("Submit"):
    st.toast(f"User Input Submitted - {user_prompt}")
    response = process_user_message(user_prompt)
    st.write(response)
