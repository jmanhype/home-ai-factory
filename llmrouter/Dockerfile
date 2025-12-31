# LLMRouter - Intelligent Model Selection
# From: https://github.com/ulab-uiuc/LLMRouter

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone LLMRouter
RUN git clone https://github.com/ulab-uiuc/LLMRouter.git /app/llmrouter

# Install Python dependencies
WORKDIR /app/llmrouter
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || \
    pip install --no-cache-dir torch transformers fastapi uvicorn httpx

# Copy our custom router service
COPY router_service.py /app/router_service.py
COPY config.yaml /app/config.yaml

WORKDIR /app

EXPOSE 4001

CMD ["python", "router_service.py"]
