FROM python:3.12-slim
WORKDIR /app

# Copy requirements and install
COPY ml-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ml-service code
COPY ml-service/ .

# Copy data-ingestion for models and features
COPY data-ingestion/models/tuned/ /data-ingestion/models/tuned/
COPY data-ingestion/data/processed/features_complete.csv /data-ingestion/data/processed/features_complete.csv

EXPOSE 5001
CMD ["python", "app.py"]