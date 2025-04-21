#!/bin/bash

# Script to set up X11 for Docker GUI applications
# This will automatically detect the user's environment and set up X11 forwarding

echo "=== Configuration de X11 pour Docker ==="

# Detect OS
OS_TYPE=$(uname -s)

# Create data directory
mkdir -p data

# Configure X11 based on OS
case "$OS_TYPE" in
    Linux)
        echo "Système Linux détecté. Configuration de X11..."
        # Allow connections from local containers
        xhost +local:docker
        
        # Check if we're in an SSH session with X11 forwarding
        if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
            echo "Session SSH détectée. Assurez-vous d'avoir activé le forwarding X11 (-X ou -Y)."
        fi
        
        # Set environment variables for docker-compose
        export DISPLAY=:0
        ;;
        
    Darwin)
        echo "Système macOS détecté. Configuration de XQuartz..."
        
        # Check if XQuartz is installed
        if ! command -v xquartz &> /dev/null; then
            echo "XQuartz n'est pas installé. Veuillez l'installer:"
            echo "brew install --cask xquartz"
            exit 1
        fi
        
        # Start XQuartz if not running
        if ! ps -e | grep -q "[X]Quartz"; then
            echo "Démarrage de XQuartz..."
            open -a XQuartz
            
            # Wait for XQuartz to start
            sleep 2
        fi
        
        # Configure XQuartz to allow connections from network clients
        defaults write org.xquartz.X11 nolisten_tcp 0
        
        # Restart XQuartz to apply settings
        killall Xquartz
        open -a XQuartz
        
        # Wait for XQuartz to restart
        sleep 3
        
        # Get IP address
        IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
        
        # Set DISPLAY environment variable
        export DISPLAY=$IP:0
        
        # Allow connections from Docker
        xhost + $IP
        ;;
        
    MINGW*|CYGWIN*)
        echo "Système Windows détecté. Configuration de X11..."
        
        # Check if X server is installed
        if ! command -v vcxsrv &> /dev/null && ! command -v xming &> /dev/null; then
            echo "Serveur X non détecté. Veuillez installer VcXsrv ou Xming."
            exit 1
        fi
        
        # Detect IP address
        IP=$(ipconfig | grep -A 5 "Ethernet adapter" | grep "IPv4" | head -n 1 | awk '{print $NF}')
        
        export DISPLAY=$IP:0.0
        echo "Définition de DISPLAY=$DISPLAY"
        ;;
        
    *)
        echo "Système non reconnu: $OS_TYPE"
        echo "Configuration manuelle requise."
        exit 1
        ;;
esac

echo "X11 configuré. Vous pouvez maintenant lancer l'application avec Docker Compose."
echo "Commande: docker-compose up --build"
echo ""
echo "Pour désactiver l'accès X11 après utilisation: xhost -local:docker"