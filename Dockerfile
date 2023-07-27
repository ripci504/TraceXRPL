FROM python:latest

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN pip install Flask==2.3.2 pydantic==2.1.1 requests==2.31.0 shortuuid==1.0.11 Werkzeug==2.3.6 celery==5.3.1 redis==4.6.0 Flask-SQLAlchemy==3.0.5 xrpl-py==2.1.0

WORKDIR /app
