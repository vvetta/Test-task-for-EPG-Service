FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    zlib1g-dev \
    libjpeg-dev \
    libtiff-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
