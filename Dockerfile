FROM python:3.8.3-alpine
#
RUN mkdir /usr/src/flask_backend/
WORKDIR /usr/src/flask_backend/
#
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#
RUN apk update
RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    libressl-dev \
    libffi-dev \
    zeromq-dev \
    git
COPY . /usr/src/flask_backend/
RUN pip install -r requirements.txt
#
ENTRYPOINT ["sh", "entrypoint.sh"]
