FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies that might be missing
RUN pip install --no-cache-dir python-multipart

# Copy the rest of the application
COPY . .

# Expose ports for FastAPI and Streamlit
EXPOSE 8000
EXPOSE 8501

# Create a script to run both services
RUN echo '#!/bin/bash\n\
if [ "$SERVICE" = "api" ]; then\n\
    uvicorn app:app --host 0.0.0.0 --port 8000\n\
elif [ "$SERVICE" = "streamlit" ]; then\n\
    streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0\n\
else\n\
    echo "Unknown service: $SERVICE"\n\
    exit 1\n\
fi' > /app/start.sh

RUN chmod +x /app/start.sh

# Set the entrypoint
ENTRYPOINT ["/app/start.sh"] 