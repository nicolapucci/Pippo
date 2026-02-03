from fastapi import (
    FastAPI
)
import requests
import uvicorn

app = FastAPI()

@app.post('/')
def main(data:dict):

    #define the dict structure and perfom action basedon data

    return



if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0',port=8000)


