FROM python:latest

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN pip install Flask flask pydantic requests shortuuid Werkzeug celery redis git+https://github.com/XRPLF/xrpl-py flask_sqlalchemy

WORKDIR /app
