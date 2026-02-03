FROM python3:11-slim

WORKDIR app/

COPY requirements.txt .

RUN pip install --no-cache -r requirements.txt

COPY app.py .

EXPOSE 8000

CMD [ "python","-u","app.py" ]