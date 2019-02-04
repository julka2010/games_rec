FROM tensorflow/tensorflow:latest-gpu-py3

WORKDIR /app
ENV LANG=C.UTF-8
COPY ./misc/start-gunicorn.sh /usr/local/bin/

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pip install pipenv && \
    pipenv install --deploy --system

COPY ./app /app
