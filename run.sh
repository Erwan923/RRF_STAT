#!/bin/bash

# Script de lancement pour RRF STAT
# Vérifie les dépendances et lance l'application

echo "=== RRF STAT - Système d'Analyse Tactique des Alertes ==="
echo "Vérification des dépendances..."

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "Python3 n'est pas installé. Veuillez l'installer."
    exit 1
fi

# Vérifier si pip est installé
if ! command -v pip3 &> /dev/null; then
    echo "pip3 n'est pas installé. Veuillez l'installer."
    exit 1
fi

# Vérifier si tkinter est disponible
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "tkinter n'est pas installé. Veuillez l'installer avec:"
    echo "sudo apt-get install python3-tk  # Sur Debian/Ubuntu"
    echo "sudo dnf install python3-tkinter  # Sur Fedora"
    exit 1
fi

# Installer les dépendances
echo "Installation des dépendances Python..."
pip3 install -r requirements.txt

# Lancer l'application
echo "Lancement de RRF STAT..."
python3 gui_zabbix.py