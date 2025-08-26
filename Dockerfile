FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY cookbook/examples/streamlit_apps/universal_agent_interface/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app/

# Copy FAPS logo to the right location
COPY logo_faps.png /app/cookbook/examples/streamlit_apps/universal_agent_interface/

# Set environment variables
ENV PYTHONPATH=/app
ENV OLLAMA_HOST=ollama:11434
ENV AGNO_TELEMETRY=false

# Expose Streamlit port
EXPOSE 8501

# Working directory for the Streamlit app
WORKDIR /app/cookbook/examples/streamlit_apps/universal_agent_interface

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]