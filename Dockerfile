FROM python:3.11-slim-buster

WORKDIR /root/word

COPY . .

RUN pip3 install --upgrade pip setuptools

RUN pip3 install -U pip && pip3 install -U -r requirements.txt

CMD ["python3","-m","word"]
