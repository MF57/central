FROM python:2.7

WORKDIR /central

COPY . .

RUN pip install flask
RUN pip install requests
CMD ["python", "central.py"]

