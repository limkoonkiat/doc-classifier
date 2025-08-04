from utils import llm


def generate_response(user_message):
    delimiter = "####"

    system_message = f"""
    You are a data classification assistant helping the company to classify documents by security and sensitivity. 
    Your task is to answer any questions related to data classification based on the provided knowledge base.
    """

    messages = [
        {'role': 'system',
         'content': system_message},
        {'role': 'user',
         'content': f"{delimiter}{user_message}{delimiter}"},
    ]

    response_to_user = llm.get_completion_by_messages(messages)
    response_to_user = response_to_user.split(delimiter)[-1]
    return response_to_user


def generate_rag_response(user_message, vector_store):
    # Build the prompt for RAG
    template = """
    You are an expert data classification assistant helping a health research and pharmaceutical company in Singapore to classify documents by security and sensitivity. 
    Use the following pieces of context to give both a security and sensitivity classification of the output as the answer.
    Security classification is based on the Security Classification Framework (SCF). Sensitivity classification is based on the External Sensitivity Framework (ESF).
    The classification of a document must include both a security and a sensitivity classifications, with the combined classification in the format: <security classification> / <sensitivity classification>. 
    If you do not know the answer, say you don't know. Do not try to make up an answer.
    In your answer, include the text of the document with the parts that can be masked to have a lower security and sensitivity classification in **bold**.
    Context: {context}
    Question: What is the security and sensitivity classification of the following text/document enclosed in delimiters?
    ####
    {question}
    ####
    Give your answer only as a valid json object containing the following information. Your output must be valid json without any additions:
        security_classification: <Your security classification here>,
        sensitivity_classification: <Your sensitivity classification here>,
        security_reasoning: <Your reasoning for your security classification here>,
        sensitivity_reasoning: <Your reasoning for your sensitivity classification here>
        document_text: <The text of the document with the parts that can be masked to have a lower security and sensitivity classification in **bold**.>
        
    """
    return llm.get_rag_completion(user_message, template, vector_store)


def process_user_message(user_message):
    reply = generate_response(user_message)
    return reply
