# Use Python 3.13 slim as base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .

# Install dependency
RUN pip install .

COPY hnpy/ hnpy/
COPY main.py .

ENTRYPOINT ["python", "main.py"]
