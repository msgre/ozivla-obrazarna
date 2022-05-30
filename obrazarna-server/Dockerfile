FROM python:3.10

RUN mkdir /app
WORKDIR /app
EXPOSE 8000

RUN apt-get update && \
    apt-get -y install vim ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/
# RUN ./manage.py collectstatic --no-input
