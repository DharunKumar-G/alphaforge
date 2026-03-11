# ---- Base image ----
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create persistent data directories
RUN mkdir -p data/db data/cache/prices

# Initialize database
RUN python scripts/init_db.py

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SQLITE_DB_PATH=data/db/alphaforge.db

# Streamlit config is in .streamlit/config.toml (port 8000, headless)

# Run the app
CMD ["streamlit", "run", "app.py", \
     "--server.port=8000", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
