import requests


ollama_base_url = 'http://ollama'


def ollama_generate(prompt):

    try:
        response = requests.post(url=f"{ollama_base_url}/generate",data={"prompt":prompt})
        
        return response
    except requests.ConnectionError as e:
        print(f"Error: {e}")



def expand_user_query(query,chat_history):
    prompt = f"""
    expand the *USER QUERY* using the context in *CHAT_HISTORY*
    # USER QUERY
    {query}

    # CHAT_HISTORY
    {chat_history}
"""
    return ollama_generate(prompt)


def rewrite_query(query,additional_data,search_type):

    query = query if not additional_data['missing_data'] else additional_data['missing_data']#is missing_data is present i wanna focus the search on that
    
    prompt = f"""
    optimize *USER QUERY* for {search_type}

    # USER QUERY
    {query}
"""
    
    return ollama_generate(prompt)



def evaluate_context(query,context):

    prompt = f"""
    evaluate if the *CONTEXT* provided is reliable and contains enough information to answer *USER QUERY*,
    if the context is enough to answer return pass:True and a confidence_score between 0 and 1.
    if the context is not enough to answer the question, return a list of missing_informations, pass:False and the confidence_score between 0 and 1.
    
    # REPONSE SAMPLE
    {{
    pass:False,
    confidence_score:0.3,
    missing_informations: [how to kill a process in linux, how to check the active processes]
    }}

    # USER QUERY
    {query}

    # CONTEXT
    {context}

    RESPONSE:"""
    
    return ollama_generate(prompt)
