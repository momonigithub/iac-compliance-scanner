FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Download and install tfsec
RUN wget -qO /usr/local/bin/tfsec https://github.com/aquasecurity/tfsec/releases/latest/download/tfsec-linux-amd64 \
    && chmod +x /usr/local/bin/tfsec

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY scanner/ ./scanner/
COPY policies/ ./policies/
COPY terraform/ ./terraform/
COPY scripts/ ./scripts/

# Ensure directories for DB and reports exist
RUN mkdir -p db reports

# Expose port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
