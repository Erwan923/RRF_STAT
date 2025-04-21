#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug script for RRF STAT Application
"""

import os
import sys
import traceback
from flask import Flask, request, session

print("=== RRF STAT Debugging Tool ===")

# Check if layout.html exists
print("\nChecking templates...")
layout_path = os.path.join("templates", "layout.html")
if os.path.exists(layout_path):
    print(f"✓ layout.html exists")
else:
    print(f"✗ ERROR: layout.html is missing - all templates depend on this file!")

# Check directories
print("\nChecking directories...")
for directory in ["data", "templates"]:
    if os.path.exists(directory) and os.path.isdir(directory):
        print(f"✓ Directory '{directory}' exists")
    else:
        print(f"✗ ERROR: Directory '{directory}' is missing")
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"  - Created directory '{directory}'")
        except Exception as e:
            print(f"  - Failed to create directory: {str(e)}")

# Check imports
print("\nChecking imports...")
try:
    from parse_zbx_problems import read_csv_file, filter_data, count_alerts, show_stats, parse_args, display_data
    print("✓ All needed functions imported from parse_zbx_problems.py")
except ImportError as e:
    print(f"✗ ERROR importing from parse_zbx_problems.py: {str(e)}")
except Exception as e:
    print(f"✗ ERROR: {str(e)}")
    traceback.print_exc()

# Check CSV file
print("\nChecking CSV file...")
csv_file = "zbx_problems_export.csv"
if os.path.exists(csv_file):
    print(f"✓ Default CSV file ({csv_file}) exists")
    try:
        from parse_zbx_problems import read_csv_file
        data = read_csv_file(csv_file)
        print(f"✓ Successfully loaded CSV with {len(data)} rows")
    except Exception as e:
        print(f"✗ ERROR loading CSV: {str(e)}")
        traceback.print_exc()
else:
    print(f"✗ ERROR: Default CSV file ({csv_file}) is missing")

# Check Flask app
print("\nChecking Flask app...")
try:
    from web_gui_zabbix import app
    print("✓ Flask app imported successfully")
    
    # Check routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(rule.endpoint)
    
    print(f"✓ Found {len(routes)} routes: {', '.join(routes)}")
    
except ImportError as e:
    print(f"✗ ERROR importing Flask app: {str(e)}")
except Exception as e:
    print(f"✗ ERROR: {str(e)}")
    traceback.print_exc()

# Check dependencies
print("\nChecking dependencies...")
dependencies = [
    "flask", "pandas", "json", "csv", "datetime", 
    "io", "contextlib", "collections", "argparse"
]

for dep in dependencies:
    try:
        __import__(dep)
        print(f"✓ {dep} is installed")
    except ImportError:
        print(f"✗ ERROR: {dep} is missing")

print("\n=== Debug Summary ===")
print("Run: python web_gui_zabbix.py to start the application")
print("Access: http://localhost:8050 in your web browser")
print("If you encounter issues, review the errors above for assistance.")