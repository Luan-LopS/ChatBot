FROM python:3.10-slim AS python-base

RUN apt-get update && apt-get install -y \
    gnupg \
    ca-certificates \
    unzip \
    curl \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

RUN ollama serve & \
    sleep 10 && \
    ollama pull gemma3:1b && \
    pkill -f 'ollama serve' || true

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "ollama serve & gunicorn -w 4 -b 0.0.0.0:8000 --access-logfile - --error-logfile - app:app"]
