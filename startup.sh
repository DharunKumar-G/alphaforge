#!/bin/bash
# Azure App Service startup script

# Create data directories (Azure's /home is persistent)
mkdir -p /home/data/db
mkdir -p /home/data/cache/prices
mkdir -p /home/data/cache

# Set the DB path to persistent Azure storage
export SQLITE_DB_PATH="/home/data/db/alphaforge.db"

# Initialize DB if it doesn't exist
python scripts/init_db.py

# Start the app on Azure's required port
streamlit run app.py \
  --server.port 8000 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false
