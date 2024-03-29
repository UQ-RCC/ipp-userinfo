FROM python:3.8.6-alpine3.12 as builder
WORKDIR /app

RUN apk update
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    g++ \
    python3-dev \
    musl-dev \
    postgresql-dev \
    linux-headers
    
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN python setup.py install
