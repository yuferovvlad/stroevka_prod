FROM python:3.8

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY table_one .

CMD ["gunicorn", "table_one.wsgi:application", "--bind", "0.0.0.0:8000"]

#FROM ubuntu:latest
#LABEL authors="yuferov"
#ENTRYPOINT ["top", "-b"]