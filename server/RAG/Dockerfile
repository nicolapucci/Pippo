FROM python3:11-slim

WORKDIR app/

COPY requirements.txt .

RUN pip install --no-cache -r requirements.txt

COPY app.py .
COPY web_search/ web_search/
COPY semantic_search/ semantic_search/
COPY LLM_interface/ LLM_interface/
COPY cleaner/ cleaner/

EXPOSE 8000

CMD [ "python","-u","app.py" ]