FROM python:2.7

WORKDIR /central

COPY . .

RUN pip install flask
CMD ["python", "central.py"]

