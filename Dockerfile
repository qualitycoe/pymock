# Use an official Python runtime as the base image
FROM python:3.13-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for building Python packages and Git
RUN apt-get update && apt-get install -y \
    git \
    make \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (for better caching)
# Copy all necessary project files
COPY pyproject.toml requirements.txt Makefile config.yaml README.md ./
COPY src/ src/
COPY tests/ tests/

# Install Hatch, create the environment, and install dependencies
RUN pip install --no-cache-dir hatch && \
    hatch env create && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install "ruleenginex @ git+https://github.com/qualitycoe/ruleenginex.git@main#egg=ruleenginex"

# Set environment variables for Hatch to use the correct environment
ENV PATH="/root/.local/share/hatch/env/virtual/pymock/default/bin:$PATH"
ENV HATCH_ENV=default

# Run tests when the container starts
CMD ["make", "test"]
