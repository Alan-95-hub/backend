
FROM python:3.8.3-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

ADD ./yandex_products /app
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install --upgrade pip

COPY requirements.txt /app

COPY docker-entrypoint.sh /app

RUN pip install -r /app/requirements.txt

RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
