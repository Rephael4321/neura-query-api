FROM python:3.9-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app/

EXPOSE 8888

ENTRYPOINT ["python3", "-B"]

CMD ["./app/main.py"]