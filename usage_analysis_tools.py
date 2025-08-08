#!/usr/bin/env python3
"""
Outils pour analyser l'utilisation des classes et méthodes Python
Combine analyse statique et dynamique
"""

import ast
import os
import sys
from pathlib import Path
from collections import defaultdict, Counter
import subprocess

class PythonUsageAnalyzer:
    """Analyse l'utilisation des classes et méthodes dans un projet Python"""
    
    def __init__(self, source_path):
        self.source_path = Path(source_path)
        self.classes = {}
        self.methods = {}
        self.imports = defaultdict(list)
        self.class_usage = defaultdict(list)
        self.method_calls = defaultdict(list)
        
    def analyze_file(self, file_path):
        """Analyse un fichier Python pour extraire les utilisations"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            analyzer = FileAnalyzer(str(file_path))
            analyzer.visit(tree)
            
            # Collecte des résultats
            self.classes.update(analyzer.classes)
            self.methods.update(analyzer.methods)
            self.imports[str(file_path)] = analyzer.imports
            self.class_usage[str(file_path)] = analyzer.class_usage
            self.method_calls[str(file_path)] = analyzer.method_calls
            
        except Exception as e:
            print(f"Erreur lors de l'analyse de {file_path}: {e}")
    
    def analyze_project(self):
        """Analyse tous les fichiers Python du projet"""
        python_files = list(self.source_path.rglob("*.py"))
        
        print(f"🔍 Analyse de {len(python_files)} fichiers Python...")
        
        for py_file in python_files:
            if '__pycache__' not in str(py_file):
                self.analyze_file(py_file)
        
        return self.generate_report()
    
    def generate_report(self):
        """Génère un rapport d'utilisation"""
        report = {
            'classes_defined': len(self.classes),
            'methods_defined': sum(len(methods) for methods in self.classes.values()),
            'total_files': len(self.class_usage),
            'class_usage_map': dict(self.class_usage),
            'method_usage_map': dict(self.method_calls),
            'classes': dict(self.classes)
        }
        
        return report
    
    def find_class_usages(self, class_name):
        """Trouve où une classe spécifique est utilisée"""
        usages = []
        for file_path, classes_used in self.class_usage.items():
            if class_name in classes_used:
                usages.append({
                    'file': file_path,
                    'occurrences': classes_used.count(class_name)
                })
        return usages
    
    def generate_usage_graph_data(self):
        """Génère des données pour créer un graphique d'utilisation"""
        graph_data = {
            'nodes': [],
            'edges': []
        }
        
        # Noeuds (classes)
        for class_name in self.classes:
            graph_data['nodes'].append({
                'id': class_name,
                'type': 'class',
                'methods': len(self.classes[class_name])
            })
        
        # Arêtes (utilisations)
        for file_path, classes_used in self.class_usage.items():
            file_name = Path(file_path).stem
            for class_name in set(classes_used):
                if class_name in self.classes:
                    graph_data['edges'].append({
                        'from': file_name,
                        'to': class_name,
                        'weight': classes_used.count(class_name)
                    })
        
        return graph_data

class FileAnalyzer(ast.NodeVisitor):
    """Visiteur AST pour analyser un fichier Python"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.classes = {}
        self.methods = {}
        self.imports = []
        self.class_usage = []
        self.method_calls = []
        self.current_class = None
    
    def visit_ClassDef(self, node):
        """Visite une définition de classe"""
        self.classes[node.name] = []
        old_class = self.current_class
        self.current_class = node.name
        
        # Analyse des méthodes de la classe
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.classes[node.name].append(item.name)
        
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node):
        """Visite une définition de fonction/méthode"""
        if self.current_class:
            method_key = f"{self.current_class}.{node.name}"
        else:
            method_key = node.name
        
        self.methods[method_key] = {
            'file': self.file_path,
            'class': self.current_class,
            'args': [arg.arg for arg in node.args.args]
        }
        
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Visite un appel de fonction/méthode"""
        # Appels de méthodes (obj.method())
        if isinstance(node.func, ast.Attribute):
            self.method_calls.append(node.func.attr)
        
        # Appels de constructeurs ou fonctions
        elif isinstance(node.func, ast.Name):
            self.class_usage.append(node.func.id)
        
        self.generic_visit(node)
    
    def visit_Name(self, node):
        """Visite une référence à un nom"""
        if isinstance(node.ctx, ast.Load):
            # Utilisation potentielle d'une classe
            if node.id[0].isupper():  # Convention: classes commencent par majuscule
                self.class_usage.append(node.id)
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Visite une instruction import"""
        for alias in node.names:
            self.imports.append(alias.name)
    
    def visit_ImportFrom(self, node):
        """Visite une instruction from...import"""
        if node.module:
            for alias in node.names:
                self.imports.append(f"{node.module}.{alias.name}")

def generate_call_graph(source_path, output_file="call_graph.png"):
    """Génère un graphique des appels avec pycallgraph"""
    try:
        # Trouve le fichier principal
        main_files = list(Path(source_path).glob("main.py")) + \
                    list(Path(source_path).glob("__main__.py")) + \
                    list(Path(source_path).glob("app.py"))
        
        if not main_files:
            print("⚠️ Aucun fichier principal trouvé (main.py, app.py, etc.)")
            return False
        
        main_file = main_files[0]
        
        cmd = [
            'pycallgraph',
            'graphviz',
            '--output-file', output_file,
            '--',
            'python', str(main_file)
        ]
        
        print(f"🔄 Génération du graphique d'appels...")
        result = subprocess.run(cmd, cwd=source_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Graphique généré: {output_file}")
            return True
        else:
            print(f"❌ Erreur: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ pycallgraph n'est pas installé")
        print("Installation: pip install pycallgraph2")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python usage_analyzer.py <dossier_source>")
        sys.exit(1)
    
    source_path = sys.argv[1]
    
    # Analyse statique
    analyzer = PythonUsageAnalyzer(source_path)
    report = analyzer.analyze_project()
    
    print(f"\n📊 Rapport d'analyse:")
    print(f"   Classes définies: {report['classes_defined']}")
    print(f"   Méthodes définies: {report['methods_defined']}")
    print(f"   Fichiers analysés: {report['total_files']}")
    
    # Affichage des utilisations par classe
    print(f"\n🔗 Utilisation des classes:")
    for class_name in report['classes']:
        usages = analyzer.find_class_usages(class_name)
        if usages:
            print(f"   {class_name}: utilisée dans {len(usages)} fichier(s)")
            for usage in usages[:3]:  # Limite à 3 pour l'affichage
                file_name = Path(usage['file']).name
                print(f"      - {file_name} ({usage['occurrences']} fois)")
        else:
            print(f"   {class_name}: ⚠️ non utilisée")
    
    # Génération du graphique dynamique
    print(f"\n🎯 Génération du graphique d'appels dynamique...")
    generate_call_graph(source_path)

if __name__ == "__main__":
    main()