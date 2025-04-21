# RRF STAT - Debug Report

## Issues Found and Fixed

1. **Missing Layout Template**
   - Problem: The application's templates (index.html, results.html, stats.html, stats_results.html) all extend from "layout.html", but this file was missing.
   - Fix: Created a new layout.html template with proper styling and structure.

2. **Import Issue in web_gui_zabbix.py**
   - Problem: The `display_data` function was imported inside a method instead of at the top of the file with other imports.
   - Note: Could not fix directly due to file permission issues, but addressed in the debug documentation.

3. **Flask Debug Mode in Production**
   - Problem: The Flask application runs with debug=True which is not recommended for production environments.
   - Resolution: Documented as an issue to be fixed.

4. **Missing Error Handling for File Operations**
   - Problem: The application lacks proper error handling for file operations and file validation.
   - Resolution: Documented as an issue to be addressed.

5. **Missing CSRF Protection**
   - Problem: Forms in the application don't have CSRF protection enabled.
   - Resolution: Documented as a security issue to be fixed.

## Other Potential Issues

1. **Documentation vs Actual Code**
   - The documentation refers to a file called `gui_zabbix.py`, but the actual file is `web_gui_zabbix.py`.

2. **Inconsistent Command-Line Arguments**
   - The command-line interface for `parse_zbx_problems.py` seems to have inconsistent argument handling.

3. **Limited Input Validation**
   - The application has limited validation for user inputs, which could lead to errors.

## How to Run the Application

1. **Run with Python directly**:
   ```bash
   python web_gui_zabbix.py
   ```
   Access at: http://localhost:8050

2. **Run with Docker**:
   ```bash
   ./run_web_docker.sh
   ```
   Access at: http://localhost:8050

## Debugging

If you encounter issues:

1. Run the debugging script to check your environment:
   ```bash
   python debug_app.py
   ```

2. Check the Flask application logs for detailed error messages.

3. Ensure all templates are properly set up in the templates directory.

4. Verify that the CSV data file is valid and properly formatted.