#!/bin/bash

# Script to run RRF STAT Web Interface in Docker
# This script handles Docker setup for the web version

echo "=== RRF STAT - Système d'Analyse Tactique des Alertes (Web) ==="
echo "Préparation de l'environnement Docker..."

# Ensure Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé. Veuillez l'installer."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Docker Compose n'est pas installé. Veuillez l'installer."
    exit 1
fi

# Create directories if not exist
mkdir -p data
mkdir -p templates

# Build and run the Docker container
echo "Démarrage de RRF STAT Web dans Docker..."

# Check if using docker-compose or docker compose (v2)
if command -v docker-compose &> /dev/null; then
    docker-compose up --build
else
    docker compose up --build
fi

echo "RRF STAT Web terminé."
