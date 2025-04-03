FROM python:3.9

# 1. Install system-level dependencies (including distutils)
RUN apt-get update && apt-get install -y \
    python3-distutils python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

# 2. Upgrade pip/setuptools (to avoid legacy issues)
RUN python -m pip install --upgrade pip setuptools

# 3. Install project dependencies
WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the code
COPY src/ /app/
COPY .env .env

# 6. Keep the container running
CMD ["tail", "-f", "/dev/null"]

