### ML Service (Python with Anaconda)
```bash
cd ml-service

# Create conda environment
conda create -n racing-ml python=3.12 -y

# Activate environment
conda activate racing-ml

# Install dependencies (we'll create requirements.txt later)
pip install -r requirements.txt

# Run service
python src/main.py
```

### Data Ingestion (Python with Anaconda)
```bash
cd data-ingestion

# Use the same conda environment
conda activate racing-ml

# Install dependencies
pip install -r requirements.txt

# Run ingestion
python src/main.py
```

### MCP Server (Python with Anaconda)
```bash
cd mcp-server

# Use the same conda environment
conda activate racing-ml

# Install dependencies
pip install -r requirements.txt

# Run server
python src/main.py
```