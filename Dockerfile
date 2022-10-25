FROM python:3.6

ENV PYTHONUNBUFFERED 1

ADD ./requirements.txt /
RUN pip install -r ./requirements.txt

RUN mkdir -p /code/app
WORKDIR /code/app

ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

# start background tasks 
python manage.py process_tasks &

gunicorn --workers=3 app.wsgi -b 0.0.0.0:8080