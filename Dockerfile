FROM python:3.8.3-alpine
RUN mkdir /usr/src/back_1/
WORKDIR /usr/src/back_1/
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add --no-cache \
        libressl-dev \
        musl-dev \
        libffi-dev \
        zeromq-dev
COPY . /usr/src/back_1/
RUN pip install -r requirements.txt
CMD [ "python", "run.py" ]