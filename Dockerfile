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

# Cloud Run uses the PORT env var, we must respect it
ENV PORT 8080
EXPOSE 8080

# Create entrypoint script safely
RUN echo '#!/bin/bash\n\
# Start FastAPI on port 8000 in the background\n\
uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
\n\
# Start Streamlit on the port provided by Cloud Run\n\
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true\n\
\n\
# Wait for any process to exit\n\
wait -n\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

CMD ["/bin/bash", "/app/entrypoint.sh"]