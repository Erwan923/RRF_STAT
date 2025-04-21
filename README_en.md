# RRF STAT - Tactical Alert Analysis System

A Zabbix alert analysis tool with a graphical interface in the colors of the French Republic, with a cyberpunk style.

![RRF STAT Screenshot](https://example.com/screenshot.png)

## Features

- Intuitive GUI with blue-white-red French flag colors
- Modern cyberpunk style
- Zabbix alert analysis from CSV export files
- Flexible filtering by multiple criteria (severity, host, team, etc.)
- Detailed statistics and visualizations
- Export results in different formats

## Installation

### Prerequisites

- Docker and Docker Compose

### Docker Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/rrf-stat.git
cd rrf-stat
```

2. Build and launch the container:
```bash
docker-compose up -d
```

3. To enable GUI display from Docker:
```bash
xhost +local:docker
```

### Manual Installation (without Docker)

1. Make sure Python 3.6+ is installed
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python gui_zabbix.py
```

## Usage

1. Start the application
2. Load a Zabbix export CSV file
3. Use filters to refine your search
4. View results or generate statistics
5. Export filtered data as needed

## Project Structure

- `gui_zabbix.py` - Main application with graphical interface
- `parse_zbx_problems.py` - Zabbix alert analysis engine
- `Dockerfile` and `docker-compose.yml` - Docker configuration
- `requirements.txt` - Python dependencies

## Sample Data

Sample CSV files are included to test the application:
- `zbx_problems_export.csv` - Complete alert export
- `alertes.csv` - Sample filtered export

## License

This project is under the MIT License.

## Contribution

Contributions are welcome. Feel free to open an issue or pull request.