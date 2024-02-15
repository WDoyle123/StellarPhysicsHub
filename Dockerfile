# Builder 
FROM python:alpine3.19 AS builder-image

# Install dependencies
RUN apk add --no-cache build-base && \
	python -m venv /opt/venv

# virtual environment setup
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runner
FROM python:alpine3.19 AS runner-image

# copy venv from the build stage
COPY --from=builder-image /opt/venv /opt/venv

RUN apk add --no-cache libstdc++ && \
    pip install --no-cache-dir pandas gunicorn flask

# Set env variables
ENV VIRTUAL_ENV=/opt/venv \ 
	PATH="/opt/venv/bin:$PATH" \
	FLASK_APP=app.py \
	FLASK_RUN_HOST=0.0.0.0

COPY . .

EXPOSE 80

# make non root user and switch to it
RUN adduser -D myuser
USER myuser

CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]

