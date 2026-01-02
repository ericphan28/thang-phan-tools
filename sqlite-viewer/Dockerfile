FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY app.py .

ENV SQLITE_DB=/data/test.db

EXPOSE 8080

CMD ["python", "app.py"]
