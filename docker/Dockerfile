FROM python:3.11

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3-distutils python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools
RUN python -m pip install --upgrade pip setuptools

# Install ffmpeg for video processing
RUN apt-get update
RUN apt-get install -y ffmpeg

# Set up working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY src/requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src /app/src
# Copy .env file
COPY .env .env

# Keep the container running
CMD ["tail", "-f", "/dev/null"]

