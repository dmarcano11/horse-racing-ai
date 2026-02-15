FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ../data-ingestion /data-ingestion

EXPOSE 5002
CMD ["python", "app.py"]