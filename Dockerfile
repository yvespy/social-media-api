FROM python:alpine3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    python3-dev \
    jpeg-dev \
    zlib-dev

RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN adduser \
    --disable-password \
    --no-create-home \
    django-user \

RUN mkdir -p /vol/web/static /vol/web/media
RUN chown -R django-user:django-user /vol/
RUN chmod -R 755 /vol/web/

USER django-user

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
