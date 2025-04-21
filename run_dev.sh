#!/bin/bash

# Development script for RRF STAT application
# This script helps run the application with proper error checking

echo "=== RRF STAT - Dev Mode ==="

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

# Check directories
for dir in "data" "templates"; do
    if [ ! -d "$dir" ]; then
        echo "Creating $dir directory..."
        mkdir -p "$dir"
    fi
done

# Check for layout.html template
if [ ! -f "templates/layout.html" ]; then
    echo "ERROR: templates/layout.html is missing!"
    echo "Run the debug_app.py script for more information."
    exit 1
fi

# Check for required Python packages
echo "Checking dependencies..."
if ! pip install -r web-requirements.txt; then
    echo "Failed to install dependencies. Please check your Python environment."
    exit 1
fi

# Run the debug app first to check for issues
echo "Running diagnostics..."
python debug_app.py

echo ""
echo "Starting RRF STAT web application..."
echo "Access the application at: http://localhost:8050"
echo "Press Ctrl+C to stop the application"
echo ""

# Run the application with FLASK_DEBUG=0 for safer operation
export FLASK_DEBUG=0
python web_gui_zabbix.py