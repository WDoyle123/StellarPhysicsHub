FROM python:3.9-alpine

WORKDIR /app

COPY . /app

RUN apk update && \
    apk add --no-cache build-base libstdc++ && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del build-base

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
