# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Streamlit port
EXPOSE 8080

# Create entrypoint script
RUN echo '#!/bin/bash\n\
# Start FastAPI on port 8000\n\
uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
\n\
# Start Streamlit on the port provided by Cloud Run (default 8080)\n\
streamlit run app.py --server.port ${PORT:-8080} --server.address 0.0.0.0\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
