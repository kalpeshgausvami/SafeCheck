FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV and other packages
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend/ml directory structured as package
COPY . /app/backend/ml/
RUN touch /app/backend/__init__.py

EXPOSE 8080

ENV PYTHONPATH=/app
ENV QDRANT_HOST=qdrant
ENV QDRANT_PORT=6333

CMD ["uvicorn", "backend.ml.serving.app:app", "--host", "0.0.0.0", "--port", "8080"]
