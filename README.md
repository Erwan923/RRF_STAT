# RRF STAT - Système d'Analyse Tactique des Alertes

Outil d'analyse des alertes Zabbix 

![Capture d'écran RRF STAT](https://example.com/screenshot.png)

## Fonctionnalités

- Analyse des alertes Zabbix depuis un fichier CSV d'export
- Filtrage flexible par multiples critères (sévérité, hôte, équipe, etc.)
- Statistiques détaillées et visualisations
- Export des résultats en différents formats

## Installation

### Prérequis

- Docker et Docker Compose

### Installation avec Docker (Recommandé)

1. Clonez ce dépôt:
```bash
git clone https://github.com/your-username/rrf-stat.git
cd rrf-stat
```

2. Utilisez le script de démarrage automatisé:
```bash
./run_docker.sh
```

Ce script va:
- Configurer les permissions X11 nécessaires
- Créer le dossier data s'il n'existe pas
- Construire et lancer le conteneur Docker
- Restaurer les permissions X11 à la fermeture

### Installation manuelle (sans Docker)

1. Assurez-vous que Python 3.6+ est installé
2. Installez les dépendances:
```bash
pip install -r requirements.txt
```
3. Exécutez l'application:
```bash
python gui_zabbix.py
```

## Utilisation

### Démarrage Rapide

1. Exécutez le script de démarrage:
```bash
./run_docker.sh
```

2. L'interface graphique s'ouvrira automatiquement

### Instructions d'utilisation

1. Chargez un fichier CSV d'export Zabbix
2. Utilisez les filtres pour affiner votre recherche
3. Visualisez les résultats dans l'onglet RECHERCHE
4. Consultez les statistiques dans l'onglet STATISTIQUES
5. Exportez les données filtrées au besoin via l'option de menu

### Mode Headless (Sans Interface Graphique)

Pour les environnements sans support d'interface graphique (serveurs, CI/CD):

```bash
./run_headless.sh zbx_problems_export.csv --format json --output resultat.json
```

Options disponibles:
- `--output <fichier>` : Spécifier un fichier de sortie
- `--format <format>` : Format (table, json, csv, detail)
- `--severite <sev>` : Filtrer par sévérité
- `--hote <hote>` : Filtrer par hôte
- `--etat <etat>` : Filtrer par état

### Résolution des problèmes Docker

Si vous rencontrez des erreurs liées à X11 ou à l'affichage:

1. Utilisez le script de configuration X11 séparément:
```bash
./setup_docker_x11.sh
```

2. Puis lancez Docker manuellement:
```bash
docker-compose up --build
```

Pour Windows et macOS, assurez-vous d'avoir un serveur X11 installé:
- Windows: VcXsrv ou Xming
- macOS: XQuartz

## Structure du projet

### Fichiers Principaux
- `gui_zabbix.py` - Application principale avec interface graphique
- `parse_zbx_problems.py` - Moteur d'analyse des alertes Zabbix

### Scripts de Déploiement
- `run_docker.sh` - Script principal pour lancer l'application avec Docker
- `setup_docker_x11.sh` - Script de configuration X11 pour Docker
- `run_headless.sh` - Exécution en mode sans interface graphique
- `run.sh` - Lancement en mode natif (sans Docker)

### Configuration Docker
- `Dockerfile` - Configuration de l'image Docker
- `docker-compose.yml` - Configuration des services Docker

### Autres
- `requirements.txt` - Dépendances Python
- `data/` - Dossier pour stocker les données exportées


## Licence

Ce projet est sous licence libre (MIT).

## Contribution

Les contributions sont les bienvenues. N'hésitez pas à ouvrir une issue ou une pull request.
