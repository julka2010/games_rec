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
COPY ./misc/requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY ./misc/start-gunicorn.sh /usr/local/bin/
COPY ./app /app

EXPOSE 8000
