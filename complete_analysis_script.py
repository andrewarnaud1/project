#!/usr/bin/env python3
"""
Analyse complète d'un projet Python:
- Diagrammes de classes (structure)
- Analyse d'utilisation (qui utilise quoi)
- Rapport détaillé
"""

import subprocess
import sys
import json
from pathlib import Path
from usage_analyzer import PythonUsageAnalyzer

def generate_complete_analysis(source_path, project_name):
    """Génère une analyse complète du projet"""
    
    print(f"🚀 Analyse complète du projet: {project_name}")
    print("=" * 50)
    
    # 1. Diagramme de classes structurel
    print("\n📋 1. Génération du diagramme de classes...")
    struct_success = generate_class_diagram_detailed(source_path, project_name)
    
    # 2. Analyse d'utilisation
    print("\n🔍 2. Analyse des utilisations...")
    analyzer = PythonUsageAnalyzer(source_path)
    usage_report = analyzer.analyze_project()
    
    # 3. Rapport combiné
    print("\n📊 3. Génération du rapport détaillé...")
    generate_detailed_report(usage_report, analyzer, project_name)
    
    # 4. Graphique d'utilisation (optionnel)
    print("\n🎯 4. Tentative de génération du graphique d'appels...")
    try_generate_call_graph(source_path)
    
    print(f"\n✅ Analyse complète terminée!")
    print(f"📁 Consultez le dossier 'analysis_output/' pour les résultats")

def generate_class_diagram_detailed(source_path, project_name):
    """Génère un diagramme de classes détaillé"""
    try:
        cmd = [
            'pyreverse',
            '-o', 'png',
            '-o', 'svg',  # Double format
            '-p', project_name,
            '-d', 'analysis_output',
            '--ignore=__pycache__,tests',
            '-A', '-S', '-m', 'y',
            '--show-associated=1',
            source_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    except FileNotFoundError:
        print("⚠️ pyreverse non disponible (pip install pylint)")
        return False

def try_generate_call_graph(source_path):
    """Tente de générer un graphique d'appels"""
    try:
        # Cherche des fichiers exécutables
        main_candidates = ['main.py', 'app.py', '__main__.py', 'run.py']
        main_file = None
        
        for candidate in main_candidates:
            if Path(source_path, candidate).exists():
                main_file = candidate
                break
        
        if main_file:
            cmd = [
                'pycallgraph',
                'graphviz',
                '--output-file', 'analysis_output/call_graph.png',
                '--max-depth', '10',
                '--',
                'python', main_file
            ]
            
            result = subprocess.run(cmd, cwd=source_path, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ Graphique d'appels généré")
            else:
                print(f"⚠️ Échec génération graphique: {result.stderr[:100]}")
        else:
            print("⚠️ Aucun fichier principal trouvé pour le graphique d'appels")
            
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("⚠️ pycallgraph non disponible ou timeout")

def generate_detailed_report(usage_report, analyzer, project_name):
    """Génère un rapport détaillé en HTML"""
    
    Path('analysis_output').mkdir(exist_ok=True)
    
    # Calculs supplémentaires
    unused_classes = []
    heavily_used_classes = []
    
    for class_name in usage_report['classes']:
        usages = analyzer.find_class_usages(class_name)
        total_usage = sum(u['occurrences'] for u in usages)
        
        if not usages:
            unused_classes.append(class_name)
        elif total_usage > 5:
            heavily_used_classes.append((class_name, total_usage))
    
    # Génération HTML
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Analyse de {project_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .section {{ margin: 30px 0; padding: 20px; border-left: 4px solid #007acc; }}
        .warning {{ background-color: #fff3cd; }}
        .success {{ background-color: #d4edda; }}
        .info {{ background-color: #d1ecf1; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .usage-high {{ color: #28a745; font-weight: bold; }}
        .usage-medium {{ color: #ffc107; }}
        .usage-none {{ color: #dc3545; }}
    </style>
</head>
<body>
    <h1>📊 Analyse complète de {project_name}</h1>
    
    <div class="section info">
        <h2>📈 Statistiques générales</h2>
        <ul>
            <li><strong>Classes définies:</strong> {usage_report['classes_defined']}</li>
            <li><strong>Méthodes définies:</strong> {usage_report['methods_defined']}</li>
            <li><strong>Fichiers analysés:</strong> {usage_report['total_files']}</li>
        </ul>
    </div>
    
    <div class="section success">
        <h2>🎯 Classes les plus utilisées</h2>
        <table>
            <tr><th>Classe</th><th>Utilisations totales</th><th>Méthodes</th></tr>
    """
    
    for class_name, usage_count in heavily_used_classes:
        method_count = len(usage_report['classes'][class_name])
        html_content += f"""
            <tr>
                <td>{class_name}</td>
                <td class="usage-high">{usage_count}</td>
                <td>{method_count}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </div>
    """
    
    if unused_classes:
        html_content += f"""
    <div class="section warning">
        <h2>⚠️ Classes potentiellement inutilisées</h2>
        <p>Ces classes ne semblent pas être utilisées dans le code analysé:</p>
        <ul>
        """
        
        for class_name in unused_classes:
            html_content += f"<li class='usage-none'>{class_name}</li>"
        
        html_content += """
        </ul>
        <p><small>Note: Cette analyse est basée sur une analyse statique. 
        Les classes peuvent être utilisées dynamiquement ou dans des tests non analysés.</small></p>
    </div>
        """
    
    # Détail par classe
    html_content += """
    <div class="section info">
        <h2>🔍 Détail par classe</h2>
        <table>
            <tr><th>Classe</th><th>Méthodes</th><th>Fichiers utilisateurs</th><th>Usage total</th></tr>
    """
    
    for class_name, methods in usage_report['classes'].items():
        usages = analyzer.find_class_usages(class_name)
        total_usage = sum(u['occurrences'] for u in usages)
        usage_files = len(usages)
        
        usage_class = 'usage-high' if total_usage > 5 else 'usage-medium' if total_usage > 0 else 'usage-none'
        
        html_content += f"""
            <tr>
                <td>{class_name}</td>
                <td>{len(methods)}</td>
                <td>{usage_files}</td>
                <td class="{usage_class}">{total_usage}</td>
            </tr>
        """
    
    html_content += """
        </table>
    </div>
    
    <div class="section">
        <h2>📋 Méthodes par classe</h2>
    """
    
    for class_name, methods in usage_report['classes'].items():
        if methods:
            html_content += f"""
            <h3>{class_name}</h3>
            <ul>
            """
            for method in methods:
                html_content += f"<li>{method}</li>"
            html_content += "</ul>"
    
    html_content += """
    </div>
    
    <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ccc;">
        <p><small>Rapport généré automatiquement par l'analyseur Python</small></p>
    </footer>
</body>
</html>
    """
    
    with open('analysis_output/rapport_analyse.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Aussi en JSON pour traitement ultérieur
    with open('analysis_output/usage_data.json', 'w', encoding='utf-8') as f:
        json.dump(usage_report, f, indent=2, ensure_ascii=False)
    
    print("✅ Rapport HTML généré: analysis_output/rapport_analyse.html")

def main():
    if len(sys.argv) < 2:
        print("Usage: python complete_analysis.py <dossier_source> [nom_projet]")
        sys.exit(1)
    
    source_path = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else Path(source_path).name
    
    generate_complete_analysis(source_path, project_name)

if __name__ == "__main__":
    main()