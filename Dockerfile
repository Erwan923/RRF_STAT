FROM python:3.9-slim

WORKDIR /app

# Install needed packages (minimal for web app)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create data directory
RUN mkdir -p /app/data

# Copy web requirements (this should contain only pandas and flask)
COPY web-requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r web-requirements.txt

# Copy Python scripts
COPY *.py .
COPY *.csv .

# Create templates directory and copy templates
RUN mkdir -p /app/templates
COPY templates/* /app/templates/

# Expose port for Flask
EXPOSE 8050

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "web_gui_zabbix.py"]
