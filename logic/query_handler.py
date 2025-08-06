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
    Use the following pieces of context to give both a security and sensitivity classification of the output as the answer, do not use other classifications not in the context.
    Security classification is based on the Security Classification Framework (SCF). Sensitivity classification is based on the External Sensitivity Framework (ESF).
    Security classifications, from lowest to highest, are: Class Light Green, Class Dark Green, Class Blue, Class Yellow (with sub-classes NA and NB), Class Orange, Class Red, Class Black.
    Sensitivity classifications, from lowest to highest, are: S1, S2, S3.
    Classifications of a document must include both security and sensitivity classifications, with the combined classification in the format: <security classification> / <sensitivity classification>. 
    
    Context: {context}
    Question: What is the security and sensitivity classification of the following text/document delimited by <Question> tag?
    
    <Question>
    {question}
    </Question>

    In your answer, include the text of the document with the parts that can be masked to have a lower security and sensitivity classification in **bold**. 
    Only when the information can be used to identify an individual or entity then will it be higher than S1. If there is no text to mask, just return the original text without any bolding.
    Think through step-by-step and provide a detailed reasoning for both security and sensitivity classifications.
    If you do not know the answer, say you don't know. Do not try to make up an answer.

    Your response must be in valid json format only, containing the following information and without any additions:
        security_classification: <Your security classification here>,
        sensitivity_classification: <Your sensitivity classification here>,
        security_reasoning: <Your reasoning for your security classification here>,
        sensitivity_reasoning: <Your reasoning for your sensitivity classification here>
        document_text: <The text of the document with the parts that can be masked to have a lower security and sensitivity classification in **bold**, or if there is no text to mask, return "N/A".>
        
    """
    return llm.get_rag_completion(user_message, template, vector_store)


def process_user_message(user_message):
    reply = generate_response(user_message)
    return reply
