FROM python:3.7.2-slim-stretch

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8000

ENV NAME World

install nginx proxy
cd into home_dashboard

CMD ["gunicorn home_dashboard.wsgi:application", "--bind 0.0.0.0:8000", "--workers 3"]