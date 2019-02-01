FROM tensorflow/tensorflow:latest-gpu-py3


#RUN apk add --no-cache postgresql-libs && \
#  apk add --no-cache --virtual .build-deps \
#    gfortran \
#    build-base \
#    freetype-dev \
#    libpng-dev \
#    openblas-dev \
#    postgresql-dev \
#    python3-dev \
#    wget

WORKDIR /app
ENV LANG=C.UTF-8
EXPOSE 8000
COPY ./misc/start-gunicorn.sh /usr/local/bin/

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pip install pipenv && \
    pipenv install --deploy --system

COPY ./app /app
