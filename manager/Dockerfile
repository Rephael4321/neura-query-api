FROM python:3.12-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY shared/requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY manager/ /usr/src/app/
COPY shared/models/ORM.py /usr/src/app/app/models
COPY shared/auth.py /usr/src/app/app
COPY shared/Status.py /usr/src/app/app
COPY shared/config.py /usr/src/app/app
COPY shared/config_log.py /usr/src/app/app
COPY shared/set_configs.py /usr/src/app/app
COPY .env /usr/src/app/app

ENTRYPOINT ["python3", "-B"]

CMD ["./app/main.py"]
