from fastapi import (
    FastAPI
)
import uvicorn
from pydantic import BaseModel
from LLM_interface.llm_interface import (
    rewrite_query,#this rewrite the user's query, using the chat history as context, to improve the semantic search
    evaluate_context,#this will evaluate if the context provided it's enough to answer the query, it provided multiple possible metadata
    expand_user_query
)
from semantic_search.semantic_search import (
    retrieve as local_retrieve#this will retrieve the data using the provided query, it can search either in local storage or via web search
)
from web_search.web_search import (
    retrieve as web_retrieve
)
from cleaner.cleaner import (
    join_and_clean#this will join all the retrieved contexts and remove the duplicates/non reliable parts
)

class RequestBody(BaseModel):
    message: str
    chat_history: list
    data: dict


app = FastAPI()
MAX_ATTEMPTS = 4

context_cache = []#<-- this will be moved in smt like redis

def get_context(query,chat_history,data):

    expanded_query = expand_user_query(query,chat_history)

    collection = data['collection'] if 'collection' in data else None    
    search_type = 'semantic_search' if collection else 'web_search'

    rewritten_query = rewrite_query(expanded_query,data)

    context = local_retrieve(rewritten_query,collection)

    context_cache.append(context)

    context = join_and_clean(context_cache)

    evaluation = evaluate_context(expanded_query,context)
  
    return context,evaluation


@app.post('/')
def main(body:RequestBody):
    message = body.message
    chat_history = body.chat_history
    data = body.data

    counter = 0
    retry = True

    while retry:
        [context,evaluation] = get_context(message,chat_history,data)

        if not evaluation['pass']:
            if counter<MAX_ATTEMPTS:
                
                data['missing_data'] = evaluation['missing_data']
                #evaluation['missing_data'] contains suggestion/queries to gather the needed data that was not included in the context
                #this will be fed to rewrite_query to help him focus on gathering this missing data
            else:
                retry=False
        else:
            retry = False
        counter +=1

    return context

if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0',port=8000)