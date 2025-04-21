#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour parser le fichier zbx_problems_export.csv et extraire les informations importantes
"""

import csv
import argparse
import re
import sys
import json
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional


def parse_tags(tags_str: str) -> Dict[str, str]:
    """Parse le champ Tags et retourne un dictionnaire"""
    if not tags_str:
        return {}
    
    pattern = r'(\w+):\s*([^,]+?)(?:,|$)'
    matches = re.findall(pattern, tags_str)
    
    return {key.strip(): value.strip() for key, value in matches}


def parse_problem(problem_str: str) -> Dict[str, str]:
    """Extrait les informations du champ Problème"""
    result = {
        'titre': '', 'condition': '', 'action': '', 'impact': ''
    }
    
    if not problem_str:
        return result
        
    match = re.match(r'\s*Alerte\s+([^:]+)\s*:', problem_str)
    if match:
        result['titre'] = match.group(1).strip()
    
    for field in ['Condition of alarm', 'Action', 'Impact']:
        pattern = f'{field}:\\s*([^\\n]+)'
        match = re.search(pattern, problem_str)
        if match:
            key = field.lower().replace(' of alarm', '')
            result[key] = match.group(1).strip()
    
    return result


def extract_hostname(host_str: str) -> str:
    """Extrait le nom d'hôte court depuis un FQDN"""
    if not host_str:
        return "N/A"
    
    # Si c'est déjà un nom court, le retourner tel quel
    if '.' not in host_str:
        return host_str
    
    # Sinon extraire la première partie du FQDN
    return host_str.split('.')[0]


def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """Lit le fichier CSV et parse son contenu"""
    if not os.path.exists(file_path):
        print(f"Erreur: Le fichier {file_path} n'existe pas.")
        sys.exit(1)
    
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Parse les tags et le problème
                row['Tags_parsed'] = parse_tags(row.get('Tags', ''))
                row['Problème_parsed'] = parse_problem(row.get('Problème', ''))
                
                # Extraction des informations des tags
                hostname = row['Tags_parsed'].get('hostname', 'N/A')
                row['hostname'] = hostname
                row['hostname_short'] = extract_hostname(hostname)
                row['team'] = row['Tags_parsed'].get('team', 'N/A')
                row['namespace'] = row['Tags_parsed'].get('namespace', 'N/A')
                
                data.append(row)
        return data
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier CSV: {e}")
        sys.exit(1)


def parse_duration_to_minutes(duration_str: str) -> int:
    """Convertit une durée (2j 5h 30m) en minutes"""
    if not duration_str:
        return 0
        
    total_minutes = 0
    
    days_match = re.search(r'(\d+)j', duration_str)
    if days_match:
        total_minutes += int(days_match.group(1)) * 24 * 60
    
    hours_match = re.search(r'(\d+)h', duration_str)
    if hours_match:
        total_minutes += int(hours_match.group(1)) * 60
    
    minutes_match = re.search(r'(\d+)m', duration_str)
    if minutes_match:
        total_minutes += int(minutes_match.group(1))
    
    return total_minutes


def filter_data(data: List[Dict[str, Any]], args: argparse.Namespace) -> List[Dict[str, Any]]:
    """Filtre les données selon les critères spécifiés"""
    filtered = data
    
    # Application des filtres simples
    filters = {
        'severite': ('Sévérité', False), 
        'hote': ('Hôte', True),
        'hostname': ('hostname', True),
        'hostname_short': ('hostname_short', True),
        'team': ('team', False),
        'namespace': ('namespace', False),
        'etat': ('État', False)
    }
    
    for arg_name, (field, partial) in filters.items():
        value = getattr(args, arg_name, None)
        if value:
            if partial:
                filtered = [row for row in filtered if value.lower() in row.get(field, '').lower()]
            else:
                filtered = [row for row in filtered if value.lower() == row.get(field, '').lower()]
    
    # Filtre par tag
    if args.tag:
        key, value = args.tag.split('=') if '=' in args.tag else (args.tag, None)
        filtered = [
            row for row in filtered 
            if key in row.get('Tags_parsed', {}) and 
            (value is None or row['Tags_parsed'][key] == value)
        ]
    
    # Filtre par texte dans le problème
    if args.texte:
        filtered = [row for row in filtered if args.texte.lower() in row.get('Problème', '').lower()]
    
    # Filtres temporels
    if args.date_debut:
        try:
            date_debut = datetime.strptime(args.date_debut, '%d/%m/%Y')
            filtered = [
                row for row in filtered 
                if datetime.strptime(row.get('Temps', '').split()[0], '%d/%m/%Y') >= date_debut
            ]
        except ValueError:
            print("Erreur: Format de date invalide pour --date-debut. Utilisez DD/MM/YYYY.")
    
    if args.date_fin:
        try:
            date_fin = datetime.strptime(args.date_fin, '%d/%m/%Y')
            filtered = [
                row for row in filtered 
                if datetime.strptime(row.get('Temps', '').split()[0], '%d/%m/%Y') <= date_fin
            ]
        except ValueError:
            print("Erreur: Format de date invalide pour --date-fin. Utilisez DD/MM/YYYY.")
    
    # Filtres de durée
    for filter_type, value in [('min', args.duree_min), ('max', args.duree_max)]:
        if value:
            minutes = parse_duration_to_minutes(value)
            if filter_type == 'min':
                filtered = [row for row in filtered if parse_duration_to_minutes(row.get('Durée', '0m')) >= minutes]
            else:
                filtered = [row for row in filtered if parse_duration_to_minutes(row.get('Durée', '0m')) <= minutes]
    
    return filtered


def display_data(data: List[Dict[str, Any]], args: argparse.Namespace) -> None:
    """Affiche les données selon le format spécifié"""
    if not data:
        print("Aucune donnée ne correspond aux critères de filtrage.")
        return
    
    if args.format == 'json':
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
        
    if args.format == 'csv':
        columns = args.columns.split(',') if args.columns else ['Sévérité', 'Temps', 'État', 'Hôte', 'Titre', 'Durée']
        print(','.join(columns))
        for row in data:
            values = []
            for col in columns:
                if col == 'Titre':
                    value = row['Problème_parsed']['titre']
                elif col in ['Condition', 'Action', 'Impact']:
                    value = row['Problème_parsed'][col.lower()]
                elif col in ['Hostname', 'Team', 'Namespace', 'hostname_short']:
                    key = col.lower() if col not in ['Hostname'] else 'hostname'
                    value = row.get(key, 'N/A')
                elif col == 'Hôte':
                    # Use the actual hostname instead of the alert manager name
                    value = row.get('hostname', row.get('Hôte', 'N/A'))
                else:
                    value = row.get(col, '')
                values.append(f'"{str(value)}"')
            print(','.join(values))
        return
        
    if args.format == 'detail':
        for i, row in enumerate(data):
            print(f"\n{'='*50}")
            print(f"Alerte {i+1}/{len(data)}")
            print(f"{'='*50}")
            print(f"Sévérité: {row.get('Sévérité', '')}")
            print(f"Temps: {row.get('Temps', '')}")
            print(f"État: {row.get('État', '')}")
            print(f"Hôte: {row.get('hostname', row.get('Hôte', 'N/A'))}")
            print(f"Hostname: {row.get('hostname', 'N/A')}")
            print(f"Hostname court: {row.get('hostname_short', 'N/A')}")
            print(f"Team: {row.get('team', 'N/A')}")
            print(f"Namespace: {row.get('namespace', 'N/A')}")
            
            # Détails du problème
            print(f"\n--- Détails du problème ---")
            print(f"Titre: {row['Problème_parsed']['titre']}")
            print(f"Condition: {row['Problème_parsed']['condition']}")
            print(f"Action: {row['Problème_parsed']['action']}")
            print(f"Impact: {row['Problème_parsed']['impact']}")
            print(f"Durée: {row.get('Durée', '')}")
            print(f"Acquitté: {row.get('Acquitté', '')}")
            
            # Tags
            print("\n--- Tags ---")
            if row.get('Tags_parsed'):
                for key, value in sorted(row.get('Tags_parsed', {}).items()):
                    print(f"  - {key}: {value}")
            else:
                print("  Aucun tag")
            
            if args.raw:
                print("\n--- Problème brut ---")
                print(row.get('Problème', ''))
            
            if i < len(data) - 1:
                try:
                    input("\nAppuyez sur Entrée pour continuer ou Ctrl+C pour quitter...")
                except KeyboardInterrupt:
                    print("\nOpération interrompue par l'utilisateur.")
                    break
        return
        
    # Format par défaut: table
    columns = args.columns.split(',') if args.columns else ['Sévérité', 'Temps', 'État', 'Hôte', 'Titre', 'Durée']
    
    # Préparer les données
    table_data = []
    for row in data:
        table_row = {}
        for col in columns:
            if col == 'Titre':
                table_row[col] = row['Problème_parsed']['titre']
            elif col in ['Condition', 'Action', 'Impact']:
                table_row[col] = row['Problème_parsed'][col.lower()]
            elif col in ['Hostname', 'Team', 'Namespace', 'hostname_short']:
                key = col.lower() if col not in ['Hostname'] else 'hostname'
                table_row[col] = row.get(key, 'N/A')
            elif col == 'Hôte':
                # Use the actual hostname instead of the alert manager name
                table_row[col] = row.get('hostname', row.get('Hôte', 'N/A'))
            else:
                table_row[col] = row.get(col, '')
        table_data.append(table_row)
    
    # Calculer les largeurs de colonnes
    col_widths = {col: len(col) for col in columns}
    for row in table_data:
        for col in columns:
            col_widths[col] = max(col_widths[col], len(str(row.get(col, ''))))
    
    # Afficher l'en-tête
    total_width = sum(col_widths.values()) + (3 * len(columns)) - 1
    print("=" * total_width)
    print(' | '.join(f"{col:{col_widths[col]}}" for col in columns))
    print("-" * total_width)
    
    # Afficher les données
    for row in table_data:
        values = [f"{str(row.get(col, '')):{col_widths[col]}}" for col in columns]
        print(' | '.join(values))
    
    print("=" * total_width)


def count_alerts(data: List[Dict[str, Any]], group_by: Optional[str] = None) -> None:
    """Compte les alertes selon un critère de groupement"""
    if not data:
        print("Aucune donnée à compter.")
        return
    
    total = len(data)
    print(f"Nombre total d'alertes: {total}")
    
    if group_by:
        counts = defaultdict(int)
        for row in data:
            if group_by == 'severite':
                key = row.get('Sévérité', 'Inconnue')
            elif group_by == 'hote':
                key = row.get('Hôte', 'Inconnu')
            elif group_by == 'etat':
                key = row.get('État', 'Inconnu')
            elif group_by == 'type':
                key = row['Problème_parsed']['titre'] or 'Inconnu'
            elif group_by == 'team':
                key = row.get('team', 'Inconnue')
            elif group_by == 'namespace':
                key = row.get('namespace', 'Inconnu')
            elif group_by == 'hostname':
                key = row.get('hostname', 'Inconnu')
            elif group_by == 'hostname_short':
                key = row.get('hostname_short', 'Inconnu')
            else:
                key = 'Autre'
            
            counts[key] += 1
        
        print(f"\nRépartition par {group_by}:")
        
        # Trier par nombre décroissant
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        max_key_width = max(len(str(key)) for key, _ in sorted_counts)
        
        for key, count in sorted_counts:
            percentage = count/total*100
            print(f"  - {str(key):{max_key_width}} : {count:4d} ({percentage:5.1f}%)")


def show_stats(data: List[Dict[str, Any]]) -> None:
    """Affiche des statistiques détaillées sur les alertes"""
    if not data:
        print("Aucune donnée pour les statistiques.")
        return
    
    print("\n=== Statistiques des alertes ===")
    
    # Nombre total d'alertes
    total = len(data)
    print(f"\nNombre total d'alertes: {total}")
    
    # Statistiques par différents critères
    for group_by in ['severite', 'hote', 'etat', 'type', 'team', 'namespace', 'hostname', 'hostname_short']:
        count_alerts(data, group_by)
    
    # Statistiques temporelles
    print("\n=== Top 5 des alertes ===")
    
    # Alertes les plus anciennes
    sorted_by_time = sorted(data, key=lambda x: x.get('Temps', ''))
    if sorted_by_time:
        print("\nAlertes les plus anciennes:")
        for i, alert in enumerate(sorted_by_time[:5]):
            print(f"  {i+1}. {alert.get('Temps', 'N/A')} - {alert['Problème_parsed']['titre']} sur {alert.get('hostname_short', 'N/A')}")
    
    # Alertes les plus longues
    sorted_by_duration = sorted(data, key=lambda x: parse_duration_to_minutes(x.get('Durée', '0m')), reverse=True)
    if sorted_by_duration:
        print("\nAlertes les plus longues:")
        for i, alert in enumerate(sorted_by_duration[:5]):
            print(f"  {i+1}. {alert.get('Durée', 'N/A')} - {alert['Problème_parsed']['titre']} sur {alert.get('hostname_short', 'N/A')}")


def parse_args() -> argparse.Namespace:
    """Parse les arguments de la ligne de commande"""
    parser = argparse.ArgumentParser(
        description='Parser pour le fichier zbx_problems_export.csv',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  ./parse_zbx_problems.py --severite "Désastre"
  ./parse_zbx_problems.py --hote "db1" --format detail
  ./parse_zbx_problems.py --hostname_short "db1" --format json
  ./parse_zbx_problems.py --tag "team=mcx" --count hote
  ./parse_zbx_problems.py --stats
  ./parse_zbx_problems.py --format csv -o alertes.csv
""")
    
    # Options principales
    parser.add_argument('-f', '--fichier', default='zbx_problems_export.csv',
                      help='Fichier CSV (défaut: zbx_problems_export.csv)')
    parser.add_argument('-o', '--output', help='Fichier de sortie pour export')
    parser.add_argument('--format', choices=['table', 'json', 'detail', 'csv'], default='table',
                      help='Format d\'affichage (défaut: table)')
    parser.add_argument('--columns', help='Colonnes à afficher (séparées par des virgules)')
    parser.add_argument('--raw', action='store_true', help='Afficher le problème brut en mode détail')
    
    # Filtres
    filters = parser.add_argument_group('Filtres')
    filters.add_argument('-s', '--severite', help='Filtrer par sévérité')
    filters.add_argument('-H', '--hote', help='Filtrer par nom d\'hôte Zabbix')
    filters.add_argument('--hostname', help='Filtrer par hostname complet (tag)')
    filters.add_argument('--hostname_short', help='Filtrer par hostname court (première partie du FQDN)')
    filters.add_argument('--team', help='Filtrer par équipe')
    filters.add_argument('--namespace', help='Filtrer par namespace')
    filters.add_argument('-e', '--etat', help='Filtrer par état (PROBLÈME, RÉSOLU, etc.)')
    filters.add_argument('-t', '--tag', help='Filtrer par tag (clé ou clé=valeur)')
    filters.add_argument('-T', '--texte', help='Filtrer par texte dans la description')
    filters.add_argument('--date-debut', help='Date de début (DD/MM/YYYY)')
    filters.add_argument('--date-fin', help='Date de fin (DD/MM/YYYY)')
    filters.add_argument('--duree-min', help='Durée minimale (ex: 1j, 5h, 30m)')
    filters.add_argument('--duree-max', help='Durée maximale (ex: 1j, 5h, 30m)')
    
    # Statistiques
    stats = parser.add_argument_group('Statistiques')
    stats.add_argument('--stats', action='store_true', help='Afficher des statistiques complètes')
    stats.add_argument('--count', '-c', 
                     choices=['severite', 'hote', 'etat', 'type', 'team', 'namespace', 'hostname', 'hostname_short'],
                     help='Compter et regrouper par critère')
    
    return parser.parse_args()


def main() -> None:
    """Fonction principale"""
    global args
    args = parse_args()
    
    # Lecture du fichier CSV
    data = read_csv_file(args.fichier)
    
    # Statistiques
    if args.stats:
        show_stats(data)
        return
    
    # Comptage
    if args.count:
        count_alerts(filter_data(data, args), args.count)
        return
    
    # Filtrage
    filtered_data = filter_data(data, args)
    
    # Affichage
    display_data(filtered_data, args)
    
    # Résumé
    print(f"\n{len(filtered_data)} alertes trouvées sur un total de {len(data)}.")


if __name__ == "__main__":
    main()