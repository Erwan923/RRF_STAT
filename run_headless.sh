#!/bin/bash

# Script pour exécuter RRF STAT en mode sans interface graphique (headless)
# Utile pour les environnements de serveur ou de CI/CD

echo "=== RRF STAT - Mode Headless ==="
echo "Ce script exécute l'analyse sans interface graphique"

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "Python3 n'est pas installé. Veuillez l'installer."
    exit 1
fi

# Vérifier les arguments
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <fichier_csv> [options]"
    echo ""
    echo "Options disponibles (facultatives):"
    echo "  --output <fichier_sortie>   Spécifier un fichier de sortie"
    echo "  --format <format>           Format de sortie (table, json, csv, detail)"
    echo "  --severite <sev>            Filtrer par sévérité"
    echo "  --hote <hote>               Filtrer par hôte"
    echo "  --etat <etat>               Filtrer par état (PROBLÈME, RÉSOLU)"
    echo ""
    echo "Exemple: $0 zbx_problems_export.csv --format json --output resultat.json --severite Élevé"
    exit 1
fi

# Construire la commande
INPUT_FILE="$1"
shift

COMMAND="python3 parse_zbx_problems.py --input \"$INPUT_FILE\""

# Ajouter les options
while [ "$#" -gt 0 ]; do
    case "$1" in
        --output)
            COMMAND="$COMMAND --output \"$2\""
            shift 2
            ;;
        --format)
            COMMAND="$COMMAND --format \"$2\""
            shift 2
            ;;
        --severite)
            COMMAND="$COMMAND --severite \"$2\""
            shift 2
            ;;
        --hote)
            COMMAND="$COMMAND --hote \"$2\""
            shift 2
            ;;
        --etat)
            COMMAND="$COMMAND --etat \"$2\""
            shift 2
            ;;
        *)
            COMMAND="$COMMAND $1"
            shift
            ;;
    esac
done

# Exécuter la commande
echo "Exécution: $COMMAND"
eval "$COMMAND"

echo "Analyse terminée!"