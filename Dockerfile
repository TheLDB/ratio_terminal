FROM python:3.10-alpine

COPY src/ src/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD [ "python3", "src/main.py" ]
