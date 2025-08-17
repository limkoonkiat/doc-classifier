import streamlit as st

from utils import llm

classify_retriever_prompt = """
    You are an AI language model assistant helping with retrieving information about how to classify an original text by security and sensitivity.
    Classifications of a document must include both security and sensitivity classifications, with the combined classification in the format: < security classification > / < sensitivity classification > .
    Your task is to read the original text, and generate up to 4 different questions that have to be answered to give both a security and sensitivity classification. These questions should help retrieve relevant documents from a vector
    database to classify the original text. By generating multiple perspectives on the original text, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search.
    Provide these questions separated by newlines.
    Original text: {question}
"""

chat_hist_retriever_prompt = """
    You are a AI language model assistant helping to retrieve relevant documents about data classification from a vector database.
    Given a chat history and the latest user question which might reference context in the chat history, \
    formulate a standalone question which can be understood without the chat history.
    The reformulated question must be useful enough to retrieve relevant context from the vector database.
    Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""

classify_prompt = """
    You are a helpful data classification assistant assisting the staff of a health research and medical insurance/savings company in Singapore to classify documents by security and sensitivity.
    Classifications of a document (delimited in <document> tags) must include both security and sensitivity classifications, with the combined classification in the format: < security classification > / < sensitivity classification > .

    <Context>
    {context}
    </Context>

    Your task is to perform the following actions:
    1. Using the Security Classification Framework (SCF) from the context, think about and provide a detailed reasoning for the security classification of the document. \
        Security classifications, from lowest to highest, are: Class Light Green, Class Dark Green, Class Blue, Class Yellow(with sub-classes NA and NB), Class Orange, Class Red, Class Black.
    2. Using the External Sensitivity Framework (ESF) from the context, think about and provide a detailed reasoning for the sensitivity classification of the document. \
        Sensitivity classifications, from lowest to highest, are: S1, S2, S3. \
        Remember, only when the information can be used to identify an individual or entity(other than the company) then will it be higher than S1.
    3. Bold and return the parts of the original text that should be annoymised to have a lower security and / or sensitivity classification. If there are no parts to annoymise, return the original text.

    Think through your tasks step-by-step and provide a detailed reasoning for both security and sensitivity classifications.
    Do not use other classifications or frameworks outside of the SCF and ESF.
    If you don't know the answer, say you don't know. Do not try to make up an answer.
    
    Your response must be in valid json format only, containing the following information:
        security_classification: < Your security classification here > ,
        sensitivity_classification: < Your sensitivity classification here > ,
        security_reasoning: < Your reasoning for your security classification here > ,
        sensitivity_reasoning: < Your reasoning for your sensitivity classification here >
        document_text: < The text of the document with the parts that can be annoymised to have a lower security and sensitivity classification in **bold**, or the original text if none. 

    Review the inputs and outputs, delimited by example tags, for extra examples.
    <Examples>
    Original Text: This is a confidential document containing personal information about John Doe, who lives at 123 Main Street, Singapore.
    Answer:
        "security_classification": "Class Blue",
        "sensitivity_classification": "S2",
        "security_reasoning": "The document contains personal information that is not publicly available but does not pose a significant risk if disclosed.",
        "sensitivity_reasoning": "The document contains an address that can be identified as belonging to a specific individual, thus requiring a higher sensitivity classification.",
        "document_text": "This is a confidential document containing personal information about **John Doe**, who lives at **123 Main Street, Singapore**."
        
    Original Text: What are the company policies regarding data handling?
    Answer:
        "security_classification": "Class Dark Green",
        "sensitivity_classification": "S1",
        "security_reasoning": "The document contains a general query, no information requiring higher security classifications has been disclosed yet.",
        "sensitivity_reasoning": "The document does not contain sensitive information.",
        "document_text": "What are the company policies regarding data handling?"

    Original Text: This report contains our company's financial data for the fiscal year 2022. Annual Revenue: $1, 000, 000. Profit: $200, 000.
    Answer:
        "security_classification": "Class Blue",
        "sensitivity_classification": "S1",
        "security_reasoning": "The document contains the company's financial information that is not publicly available.",
        "sensitivity_reasoning": "The document contains the company's financial data, not the financial data of individuals or other entities besides the company.",
        "document_text": "This report contains our company's financial data for the fiscal year **2022**. **Annual Revenue: $1,000,000. Profit: $200,000**."

    Original Text: Minutes from the last board meeting held on 1st January 2023. Chairman has approved the proposal for expansion into new markets.
    Answer:
        "security_classification": "Class Yellow (NB)",
        "sensitivity_classification": "S1",
        "security_reasoning": "The document contains information about a board meeting that is not publicly available yet. The information might cause serious damage to the company when disclosed, but not very serious enough to warrant a higher security classification yet.",
        "sensitivity_reasoning": "The document contains information about a board meeting that is not publicly available, but does not contain any information that can negatively impact individuals or other entities besides the company.",
        "document_text": "Minutes from the last board meeting held on **1st January 2023**. **Chairman has approved the proposal for expansion into new markets.**"

    Original Text: We will have a teambuilding event next week, Mon, 2PM-5PM at the event hall.
    Answer:
        "security_classification": "Class Dark Green",
        "sensitivity_classification": "S1",
        "security_reasoning": "The document contains information about a staff event, which will not negatively affect the compant even if disclosed.",
        "sensitivity_reasoning": "The document does not contain sensitive information.",
        "document_text": "We will have a teambuilding event next week, Mon, 2PM-5PM at the event hall."

    Original Text: The password for the company database is 'password123'. Please do not share it with anyone.
    Answer:
        "security_classification": "Class Yellow (NA)",
        "sensitivity_classification": "S1",
        "security_reasoning": "The document contains sensitive information that, if disclosed, could lead to unauthorized access to the company's database.",
        "sensitivity_reasoning": "The document contains sensitive information that could lead to unauthorized access to the company's database, but does not cause damage to individuals or other entities besides the company directly. If the database contains personal information of customers and other entities, then the sensitivity classification would be higher.",
        "document_text": "The password for the company database is **'password123'**. Please do not share it with anyone."

    Original Text: Welcome to our service center, Ms Watts. Please look for Mr Smith at counter 6, who will be happy to guide you through the process to sign the documents. Thank you.
    Answer:
        "security_classification": "Class Dark Green",
        "sensitivity_classification": "S2",
        "security_reasoning": "The document contains information about a public interaction with a customer, and the name of a company employee, which the customer can choose to disclose anyway without any control by the company.",
        "sensitivity_reasoning": "The document only contains the name of a customer, which might affect the customer slightly if disclosed.",
        "document_text": "Welcome to our service center, **Ms Watts**. Please look for **Mr Smith** at counter 6, who will be happy to guide you through the process to sign the documents. Thank you."
    </Examples>
    
    
    <document>
    {question}
    </document>
    """

qna_prompt = """
    You are a helpful data classification assistant helping to answer questions from staff about security and sensitivity classifications of data/information/documents, 
    within a health research and medical insurance/savings company in Singapore.
    Security classification is based on the Security Classification Framework(SCF) only. Sensitivity classification is based on the External Sensitivity Framework(ESF) only.
    Classifications of a document must include both security and sensitivity classifications, with the combined classification in the format: < security classification > / < sensitivity classification > .
    Security classifications, from lowest to highest, are: Class Light Green, Class Dark Green, Class Blue, Class Yellow(with sub-classes NA and NB), Class Orange, Class Red, Class Black.
    Sensitivity classifications, from lowest to highest, are: S1, S2, S3.
    Do not use other classifications or frameworks outside of the SCF and ESF.

    <Context>
    {context}
    </Context>

    Your task is to answer any questions related to data classification based on the provided context and the conversation.
    Think through your answer step-by-step, with detailed reasoning for each step, before finalising your response.
    If you don't know the answer, say you don't know. Do not try to make up an answer.
    """


def generate_qna_response(user_input):
    chat_hist = []
    for message in st.session_state.qna_messages:
        if message["role"] == "user":
            chat_hist.append(("user", message["content"]))
        else:
            chat_hist.append(("assistant", message["content"]))
    response_to_user = llm.get_qa_completion(chat_hist_retriever_prompt,
                                             qna_prompt, user_input, chat_hist)
    return response_to_user


def generate_rag_response(user_input):
    return llm.get_classification_completion(classify_retriever_prompt, classify_prompt, user_input)
