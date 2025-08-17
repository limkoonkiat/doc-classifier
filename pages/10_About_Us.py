import streamlit as st
import pandas as pd

from utils.access import check_password


if not check_password():
    st.stop()


st.title("About Us")

st.header("Project Scope", divider="grey")

st.subheader("Problem Statement")
st.write(
    """In the course of work, officers are required to classify materials according to their security and sensitivity levels.
    However, accurate classification can be challenging due to the volume of documents and the nuanced nature of their content.
    Currently, there is no automated verification tool to validate these security and sensitivity classifications,
    leading to potential misclassifications and security risks.
    """
)

st.subheader("Project Objective")
st.write("""We propose developing an intelligent data classification tool that will:""")

st.write("1. Analyse document content to recommend appropriate security and sensitivity classifications.")

st.write("2. Provide guidance on requirements and procedures for downgrading classification levels when necessary.")

st.write("3. Serve as a knowledge base for general enquiries regarding security and sensitivity classification protocols.")

st.header("Data Sources", divider="grey")
st.write("""Due to security considerations, we used a mock data security and sensitivity classification guide to serve as the knowledge base
         in place of the actual guide, as a proof of concept for this project.
        The mock guide is based on the actual security and sensitivity classification guide but with a fictional classification system and
        modified categories and examples for each classification.
    """)

st.write("""In place of our actual organisation, this project is designed for a fictional large health research and pharmaceutical company
         with medical insurance/savings business components, serving millions of customers.""")

st.write("""We have the Security Classification Framework for assessing security classifications, and the External Sensitivity Framework for assessing sensitivity classifications.
         Security classifications focuses on the potential damage to the company and public health and safety if disclosed, while sensitivity classifications focuses on the potential damage to individuals or external entities if disclosed.
         Classifications of data/documents have to include both frameworks, e.g. *Class Blue/S1*
         """)

st.write("The mock classifications, from least to most severe, are:")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.write("**Security Classification Framework (SCF)**")
        scf = {"Classification": ["Class Light Green", "Class Dark Green", "Class Blue",
                                  "Class Yellow (NA)", "Class Yellow (NB)", "Class Orange", "Class Red", "Class Black"],
               "Usage": ["Suitable and useful to be publicly disclosed.",
                         "Unsuitable or not useful to be publicly disclosed.",
                         "Some damage to the Company and our partners if discllosed",
                         "Some damage to public health and safety, or serious damage to the Company if disclosed",
                         "Serious damage to the Company with no damage to public health and safety if disclosed",
                         "Serious damage to public health and safety, or exceptionally grave damage to the Company if disclosed",
                         "Excceptionally grave damage to public health and safety if disclosed.",
                         "Global catastrophe and societal collapse if disclosed."]}
        df_scf = pd.DataFrame(scf)
        st.markdown(df_scf.style.hide(axis="index").to_html(),
                    unsafe_allow_html=True)


with col2:
    with st.container(border=True):
        st.write("**External Sensitivity Framework (ESF)**")
        esf = {"Classification": ["S1", "S2", "S3"],
               "Usage": ["No damage to individuals or external entities if disclosed.",
                         "Some damage to individuals or external entities if disclosed.",
                         "Serious damage to individuals or external entities if disclosed."]}
        df_esf = pd.DataFrame(esf)
        st.markdown(df_esf.style.hide(axis="index").to_html(),
                    unsafe_allow_html=True)

st.header("Features", divider="grey")

st.subheader("1. Data Classification Assistant")

st.write("""
         Found on the Main page, this feature assists users in classifying documents based on their security and sensitivity requirements.
         1. Users can input text, or upload simple txt and docx files for classification.""")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.image("images/text_input.png", caption="Text Input")

with col2:
    with st.container(border=True):
        st.image("images/file_input.png", caption="File Input")

st.write("""
         2. Users click submit.
         3. The assistant will return the recommended security and sensitivity classifications, along with a detailed reasoning for the classifications.
        """)
with st.container(border=True):
    st.image("images/classification_results.png",
             caption="Classification Results")

st.write("""
         4. The assistant will also return the parts of the text that are potentially causing higher security and/or sensitivity classifications in bold.
        """)

with st.container(border=True):
    st.image("images/downgrade_your_classification.png",
             caption="Review the potentially damaging parts of the text")

st.write("""         
         5. (For text input or txt files only) With a simple integration with Govtech's Cloak, users can mask specific Personally Identifiable Information in the text as one of the ways
         to lower the security and/or sensitivity classifications. 
         Note: Current implementation is limited to basic PIIs.
         Further customisations and improvements of this feature can be explored in future iterations.
         """)

with st.container(border=True):
    st.image("images/cloak_it.png", caption="Mask PIIs with Cloak")

st.subheader("2. Q&A Assistant")

st.write("""
         Found on the Q&A page, this feature assists users by answering questions related to data classification.
         1. Users can type their questions into a chat interface.
         2. The assistant will process the questions and provide relevant answers about the classification frameworks.
         """)

with st.container(border=True):
    st.image("images/qna_input.png",
             caption="Chat session with the Q&A Assistant")

st.subheader("Future Enhancements")

st.write("""Due to the limited timeframe, we have several enhancements that we would like to implement in the future to meet our initial vision for this project:""")
st.write("""1. Improve the knowledge base to include more comprehensive, detailed and real information on security and sensitivity classifications.""")
st.write("""2. Expand support for more common file formats, including upgrading the assistant's ability to understand and process more complex documents than just simple text.""")
st.write("""3. Provide customisable settings for Cloak's anonymisation options, allowing users to choose which types of Personally Identifiable Information to anonymise and how to anonymise them.""")
st.write("""4. Implement more comprehensive downgrading of classifications, besides masking PIIs.""")
st.write("""5. Automated classification of data and documents, such as through integration with other applications.""")
