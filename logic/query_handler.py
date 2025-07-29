from helper_functions import llm

def generate_response(user_message):
    delimiter = "####"

    system_message = f"""

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

def process_user_message(user_input):
    reply = generate_response(user_input)
    return reply