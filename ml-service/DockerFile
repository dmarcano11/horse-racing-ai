FROM python:3.12-slim
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ml-service code
COPY . .

# Copy data-ingestion for model + feature access
COPY ../data-ingestion /data-ingestion

EXPOSE 5001
CMD ["python", "app.py"]