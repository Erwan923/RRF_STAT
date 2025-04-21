#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface web pour l'analyse des alertes Zabbix
Projet RRF STAT - République Française
Version adaptée pour un accès via navigateur web
"""

import os
import sys
import json
import csv
import io
from datetime import datetime
from contextlib import redirect_stdout
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session

# Importer les fonctions d'analyse depuis le script existant
from parse_zbx_problems import read_csv_file, filter_data, count_alerts, show_stats, parse_args

# Créer l'application Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Requis pour les sessions et les messages flash

# Configuration
DEFAULT_CSV = "zbx_problems_export.csv"
DATA_DIR = "data"

# Variables globales
global_data = None

# Style Cyberpunk aux couleurs de la France
class CyberpunkStyle:
    """Classe pour définir les couleurs cyberpunk aux couleurs de la France"""
    
    # Couleurs du drapeau français
    BLEU = "#0055A4"
    BLANC = "#FFFFFF"
    ROUGE = "#EF4135"
    
    # Couleurs complémentaires cyberpunk
    NOIR = "#000000"
    GRIS_FONCE = "#222222"
    BLEU_NEON = "#00FFFF"
    ROUGE_NEON = "#FF0055"

# Créer les dossiers nécessaires
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/')
def index():
    """Page d'accueil"""
    # Options pour les combobox
    etats = ["PROBLÈME", "RÉSOLU"]
    severites = ["Information", "Avertissement", "Moyen", "Élevé", "Désastre"]
    count_options = ['severite', 'hote', 'etat', 'type', 'team', 'namespace', 'hostname', 'hostname_short']
    formats = ['table', 'json', 'detail', 'csv']
    
    # Récupérer la liste des fichiers CSV disponibles
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    csv_files += [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    
    # Valeurs par défaut
    default_columns = "Sévérité,Temps,État,Hôte,Titre,Durée"
    
    return render_template(
        'index.html',
        style=CyberpunkStyle,
        csv_files=csv_files,
        default_csv=DEFAULT_CSV,
        etats=etats,
        severites=severites,
        count_options=count_options,
        formats=formats,
        default_columns=default_columns,
        data_loaded=(global_data is not None)
    )

@app.route('/load_csv', methods=['POST'])
def load_csv():
    """Charger un fichier CSV"""
    global global_data
    
    # Récupérer le chemin du fichier depuis le formulaire
    csv_path = request.form.get('csv_path', DEFAULT_CSV)
    
    # Vérifier si un fichier a été téléchargé
    if 'csv_file' in request.files and request.files['csv_file'].filename != '':
        uploaded_file = request.files['csv_file']
        file_path = os.path.join(DATA_DIR, uploaded_file.filename)
        uploaded_file.save(file_path)
        csv_path = file_path
    
    # Charger le fichier CSV
    try:
        global_data = read_csv_file(csv_path)
        flash(f"Fichier CSV chargé avec succès. {len(global_data)} alertes trouvées.", "success")
    except Exception as e:
        flash(f"Erreur lors du chargement du fichier CSV: {str(e)}", "error")
    
    return redirect(url_for('index'))

@app.route('/apply_filters', methods=['POST'])
def apply_filters():
    """Appliquer les filtres et afficher les résultats"""
    global global_data
    
    if global_data is None:
        flash("Veuillez d'abord charger un fichier CSV.", "warning")
        return redirect(url_for('index'))
    
    # Créer un Namespace pour simuler les arguments
    args = parse_args()
    
    # Récupérer les filtres depuis le formulaire
    args.severite = request.form.get('severite', '')
    args.hote = request.form.get('hote', '')
    args.hostname = request.form.get('hostname', '')
    args.hostname_short = request.form.get('hostname_short', '')
    args.team = request.form.get('team', '')
    args.namespace = request.form.get('namespace', '')
    args.etat = request.form.get('etat', '')
    args.tag = request.form.get('tag', '')
    args.texte = request.form.get('texte', '')
    args.date_debut = request.form.get('date_debut', '')
    args.date_fin = request.form.get('date_fin', '')
    args.duree_min = request.form.get('duree_min', '')
    args.duree_max = request.form.get('duree_max', '')
    args.format = request.form.get('format', 'table')
    args.columns = request.form.get('columns', 'Sévérité,Temps,État,Hôte,Titre,Durée')
    
    # Filtrer les données
    filtered_data = filter_data(global_data, args)
    
    # Capturer la sortie de la fonction display_data
    f = io.StringIO()
    with redirect_stdout(f):
        from parse_zbx_problems import display_data
        display_data(filtered_data, args)
        print(f"\n{len(filtered_data)} alertes trouvées sur un total de {len(global_data)}.")
    
    # Sauvegarder les résultats et les filtres dans la session
    session['results'] = f.getvalue()
    session['filters'] = {
        'severite': args.severite,
        'hote': args.hote,
        'hostname': args.hostname,
        'hostname_short': args.hostname_short,
        'team': args.team,
        'namespace': args.namespace,
        'etat': args.etat,
        'tag': args.tag,
        'texte': args.texte,
        'date_debut': args.date_debut,
        'date_fin': args.date_fin,
        'duree_min': args.duree_min,
        'duree_max': args.duree_max,
        'format': args.format,
        'columns': args.columns
    }
    
    # Convertir les données pour l'affichage en tableau
    if args.format == 'table':
        columns = args.columns.split(',')
        table_data = []
        for row in filtered_data:
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
                    table_row[col] = row.get('hostname', row.get('Hôte', 'N/A'))
                else:
                    table_row[col] = row.get(col, '')
            table_data.append(table_row)
        session['table_data'] = {
            'columns': columns,
            'data': table_data
        }
    
    return redirect(url_for('results'))

@app.route('/results')
def results():
    """Afficher les résultats"""
    if 'results' not in session:
        flash("Aucun résultat à afficher. Veuillez d'abord appliquer des filtres.", "warning")
        return redirect(url_for('index'))
    
    results = session.get('results', '')
    filters = session.get('filters', {})
    table_data = session.get('table_data', None)
    
    return render_template(
        'results.html',
        style=CyberpunkStyle,
        results=results,
        filters=filters,
        table_data=table_data
    )

@app.route('/stats')
def stats():
    """Afficher les statistiques"""
    global global_data
    
    if global_data is None:
        flash("Veuillez d'abord charger un fichier CSV.", "warning")
        return redirect(url_for('index'))
    
    # Options pour les combobox
    count_options = ['severite', 'hote', 'etat', 'type', 'team', 'namespace', 'hostname', 'hostname_short']
    
    return render_template(
        'stats.html',
        style=CyberpunkStyle,
        count_options=count_options,
        data_loaded=(global_data is not None)
    )

@app.route('/show_full_stats', methods=['POST'])
def show_full_stats():
    """Afficher des statistiques complètes"""
    global global_data
    
    if global_data is None:
        flash("Veuillez d'abord charger un fichier CSV.", "warning")
        return redirect(url_for('stats'))
    
    # Capturer la sortie de la fonction show_stats
    f = io.StringIO()
    with redirect_stdout(f):
        show_stats(global_data)
    
    # Sauvegarder les résultats dans la session
    session['stats_results'] = f.getvalue()
    
    return redirect(url_for('stats_results'))

@app.route('/count_by_criteria', methods=['POST'])
def count_by_criteria():
    """Compter les alertes par critère"""
    global global_data
    
    if global_data is None:
        flash("Veuillez d'abord charger un fichier CSV.", "warning")
        return redirect(url_for('stats'))
    
    # Récupérer le critère de groupement
    criteria = request.form.get('count_by', '')
    
    if not criteria:
        flash("Veuillez sélectionner un critère de groupement.", "warning")
        return redirect(url_for('stats'))
    
    # Créer un Namespace pour simuler les arguments
    args = parse_args()
    
    # Récupérer les filtres actuels s'ils existent
    filters = session.get('filters', {})
    args.severite = filters.get('severite', '')
    args.hote = filters.get('hote', '')
    args.hostname = filters.get('hostname', '')
    args.hostname_short = filters.get('hostname_short', '')
    args.team = filters.get('team', '')
    args.namespace = filters.get('namespace', '')
    args.etat = filters.get('etat', '')
    args.tag = filters.get('tag', '')
    args.texte = filters.get('texte', '')
    args.date_debut = filters.get('date_debut', '')
    args.date_fin = filters.get('date_fin', '')
    args.duree_min = filters.get('duree_min', '')
    args.duree_max = filters.get('duree_max', '')
    
    # Filtrer les données
    filtered_data = filter_data(global_data, args)
    
    # Capturer la sortie de la fonction count_alerts
    f = io.StringIO()
    with redirect_stdout(f):
        count_alerts(filtered_data, criteria)
    
    # Sauvegarder les résultats et le critère dans la session
    session['stats_results'] = f.getvalue()
    session['count_criteria'] = criteria
    
    return redirect(url_for('stats_results'))

@app.route('/stats_results')
def stats_results():
    """Afficher les résultats des statistiques"""
    if 'stats_results' not in session:
        flash("Aucun résultat à afficher. Veuillez d'abord générer des statistiques.", "warning")
        return redirect(url_for('stats'))
    
    results = session.get('stats_results', '')
    criteria = session.get('count_criteria', '')
    
    return render_template(
        'stats_results.html',
        style=CyberpunkStyle,
        results=results,
        criteria=criteria
    )

@app.route('/export_results', methods=['POST'])
def export_results():
    """Exporter les résultats"""
    global global_data
    
    if global_data is None:
        flash("Veuillez d'abord charger un fichier CSV.", "warning")
        return redirect(url_for('index'))
    
    # Récupérer le format et le nom du fichier
    export_format = request.form.get('export_format', 'csv')
    filename = request.form.get('filename', f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    
    # Ajouter l'extension si nécessaire
    if not filename.endswith(f'.{export_format}'):
        filename = f"{filename}.{export_format}"
    
    # Créer un Namespace pour simuler les arguments
    args = parse_args()
    
    # Récupérer les filtres actuels
    filters = session.get('filters', {})
    args.severite = filters.get('severite', '')
    args.hote = filters.get('hote', '')
    args.hostname = filters.get('hostname', '')
    args.hostname_short = filters.get('hostname_short', '')
    args.team = filters.get('team', '')
    args.namespace = filters.get('namespace', '')
    args.etat = filters.get('etat', '')
    args.tag = filters.get('tag', '')
    args.texte = filters.get('texte', '')
    args.date_debut = filters.get('date_debut', '')
    args.date_fin = filters.get('date_fin', '')
    args.duree_min = filters.get('duree_min', '')
    args.duree_max = filters.get('duree_max', '')
    args.format = export_format
    args.columns = filters.get('columns', 'Sévérité,Temps,État,Hôte,Titre,Durée')
    
    # Filtrer les données
    filtered_data = filter_data(global_data, args)
    
    # Chemin du fichier d'export
    export_path = os.path.join(DATA_DIR, filename)
    
    try:
        # Exporter selon le format
        if export_format == 'json':
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, indent=2, ensure_ascii=False)
        else:  # CSV par défaut
            columns = args.columns.split(',')
            with open(export_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                for row in filtered_data:
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
                            value = row.get('hostname', row.get('Hôte', 'N/A'))
                        else:
                            value = row.get(col, '')
                        values.append(value)
                    writer.writerow(values)
        
        flash(f"Les données ont été exportées avec succès dans {export_path}.", "success")
        
        # Télécharger le fichier
        return send_file(export_path, as_attachment=True)
    except Exception as e:
        flash(f"Erreur lors de l'exportation: {str(e)}", "error")
        return redirect(url_for('results'))

@app.route('/reset_filters', methods=['POST'])
def reset_filters():
    """Réinitialiser les filtres"""
    if 'filters' in session:
        session.pop('filters')
    if 'results' in session:
        session.pop('results')
    if 'table_data' in session:
        session.pop('table_data')
    
    flash("Les filtres ont été réinitialisés.", "success")
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Démarrer l'application Flask
    app.run(host='0.0.0.0', port=8050, debug=True)
