Voici votre fichier modifié avec la bibliothèque `rich` pour un meilleur rendu dans le terminal :

```python
#!/usr/bin/env python3

import argparse
from datetime import datetime
import glob
import os
import pathlib
import pytest
import requests
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from simulateur.enums import Status
from simulateur.run_tests_via_yaml import TestAPI
from utils.utils import load_config_files
from utils.yaml_loader import load_yaml_file

# Initialisation de Rich Console
console = Console()

# Vérification des variables obligatoires
URL_API = os.environ.get('URL_API')
SIMU_OUTPUT = os.environ.get('SIMU_OUTPUT', '/tmp')
LECTURE = os.environ.get('LECTURE', 'false').lower()
INSCRIPTION = os.environ.get('INSCRIPTION', 'false').lower()


def check_required_variables():
    """Vérifie que les variables d'environnement obligatoires sont définies"""
    required_vars = {
        'URL_API': URL_API,
        'SIMU_OUTPUT': SIMU_OUTPUT
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        console.print(f"[red]❌ Variables manquantes: {', '.join(missing_vars)}[/red]")
        return False
    
    console.print("[green]✓[/green] Variables d'environnement vérifiées")
    return True


def get_scenario_last_execution(identifiant: str):
    """Récupère le statut de la dernière exécution d'un scénario"""
    if not identifiant:
        return None
    
    if not URL_API:
        console.print("[red]❌ URL_API non définie[/red]")
        return None
    
    url = f"{URL_API}/injapi/last_execution/{identifiant}"
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("Récupération du statut...", total=None)
            response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            console.print(f"[yellow]⚠️ Statut HTTP: {response.status_code}[/yellow]")
            return None

        response_json = response.json()
        execution = response_json.get('execution')
        
        if not execution:
            return None
        
        return execution.get('status', None)
    
    except Exception as e:
        console.print(f"[red]❌ Erreur: {str(e)}[/red]")
        return None


def get_scenario_info_from_api(scenario_name):
    """Récupère les informations d'un scénario depuis l'API"""
    scenario_id = get_indentifiant_from_scenario_name(scenario_name)
    url = f"{URL_API}/injapi/scenario/{scenario_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        console.print(f"[red]❌ Erreur API: {str(e)}[/red]")
    
    return None


def get_json_execution(scenario_name: str):
    """Récupère le fichier JSON d'exécution d'un scénario"""
    root_dir = SIMU_OUTPUT
    
    if LECTURE == 'true':
        api_response = get_scenario_info_from_api(scenario_name)
        if api_response is None:
            return None
        
        root_dir = f"{root_dir}/{api_response.get('application').get('nom')}"
        scenario_name = api_response.get('nom')

    today_report_folder = f'{root_dir}/{scenario_name}/{datetime.now().date()}'
    last_report_folder = max(pathlib.Path(today_report_folder).glob('*/'), key=os.path.getmtime)
    json_path = f"{str(last_report_folder)}/scenario.json"
    
    return load_yaml_file(json_path)


def post_execution_result_in_isac(scenario_name: str, json_execution: dict = None):
    """Envoie les résultats d'exécution dans ISAC"""
    if INSCRIPTION != 'true':
        return

    if not URL_API:
        console.print("[yellow]⚠️ URL_API non définie, impossible de sauvegarder[/yellow]")
        return

    url = f"{URL_API}/injapi/scenario/execution"
    
    if json_execution is None:
        json_execution = get_json_execution(scenario_name)
    
    if json_execution is None:
        console.print("[red]❌ Fichier JSON introuvable[/red]")
        return

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "text/plain",
    }

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("Sauvegarde dans ISAC...", total=None)
            response = requests.post(url, headers=headers, timeout=10, json=json_execution)
        
        if response.status_code != 201:
            console.print(f"[red]❌ Échec sauvegarde (code {response.status_code})[/red]")
            return
        
        console.print("[green]✓ Résultat sauvegardé dans ISAC[/green]")
    
    except Exception as e:
        console.print(f"[red]❌ Erreur sauvegarde: {str(e)}[/red]")


def get_indentifiant_from_scenario_name(scenario: str):
    """Récupère l'identifiant d'un scénario depuis son fichier de configuration"""
    work_dir = str(pathlib.Path().resolve())
    config_file = f"{work_dir}/config/scenarios/{scenario}.conf"
    configuration = load_yaml_file(config_file)
    return configuration.get('identifiant', None)


def run_generated_test(work_dir: str, scenario_name: str):
    """Exécute un test généré en Python"""
    file_path = f"{work_dir}/scenarios/python/{scenario_name}.py"
    result = pytest.main(["-x", "-s", file_path])

    if result != 0:
        scenario_id = get_indentifiant_from_scenario_name(scenario_name)
        
        if not scenario_id:
            console.print("[red]❌ Identifiant introuvable dans la configuration[/red]")
            return False
        
        last_execution_status = get_scenario_last_execution(scenario_id)
        
        if last_execution_status is None:
            return False
        
        if last_execution_status in [Status.SUCCESS.value, Status.WARNING.value]:
            console.print("[yellow]🔄 Relance du scénario...[/yellow]")
            result = pytest.main(["-x", "-s", file_path])
            
            if result != 0:
                return False
    
    return result == 0


def run_exadata_test(work_dir: str, scenario_name: str):
    """Exécute un test Exadata"""
    os.environ['chemin_images_exadata'] = f"{work_dir}/scenarios_exadata/images/{scenario_name}"
    file_path = f"{work_dir}/scenarios_exadata/{scenario_name}.py"
    result = pytest.main(["-x", "-s", file_path])
    return result == 0


def run_yaml_test(scenario_name: str, scenario_yaml: dict):
    """Exécute un test basé sur un fichier YAML"""
    scenario_config = load_config_files(scenario_name)
    test_api_runner = TestAPI(scenario_yaml, scenario_config)
    return test_api_runner.run()


def run_scenario(scenario_name: str, work_dir: str, exadata: bool = None):
    """Exécute un scénario de test"""
    console.print(Panel(f"[bold cyan]🚀 Exécution du scénario: {scenario_name}[/bold cyan]"))
    
    is_success = False
    json_execution = None
    scenario_yaml = None

    os.environ['SCENARIO'] = scenario_name

    if exadata:
        console.print("[blue]📊 Mode Exadata[/blue]")
        is_success = run_exadata_test(work_dir, scenario_name)
    else:
        yaml_file_path = f"scenarios/yaml/{scenario_name}.yaml"
        
        with open(yaml_file_path) as f:
            scenario_yaml = yaml.safe_load(f)

        if scenario_type := scenario_yaml.get('type'):
            if scenario_type == 'API':
                console.print("[blue]🔌 Test API[/blue]")
                is_success, json_execution = run_yaml_test(scenario_name, scenario_yaml)
        else:
            console.print("[blue]🐍 Test Python généré[/blue]")
            is_success = run_generated_test(work_dir, scenario_name)

    try:
        post_execution_result_in_isac(scenario_name, json_execution)
    except Exception as e:
        console.print(f"[red]❌ Erreur ISAC: {str(e)}[/red]")
        raise TimeoutError('Impossible de sauvegarder le résultat dans ISAC!', str(e))
    
    return is_success


def run_multi_scenarios(scenarios_dir: str):
    """Exécute plusieurs scénarios"""
    console.print(Panel("[bold cyan]🎯 Exécution de tous les scénarios[/bold cyan]"))
    
    failed_tests = []
    scenarios_files = glob.glob(f"{scenarios_dir}/*.py")
    
    # Tableau des résultats
    table = Table(title="Résultats des tests")
    table.add_column("Scénario", style="cyan")
    table.add_column("Résultat", style="bold")
    
    for file_path in scenarios_files:
        scenario = file_path.split('/')[-1].split('.')[0]
        os.environ['SCENARIO'] = scenario
        
        console.print(f"\n[cyan]▶️ Test: {scenario}[/cyan]")
        result = pytest.main(["-x", "-s", file_path])
        
        if result == 0:
            table.add_row(scenario, "[green]✅ OK[/green]")
        else:
            failed_tests.append(scenario)
            table.add_row(scenario, "[red]❌ KO[/red]")
    
    console.print("\n")
    console.print(table)
    
    if failed_tests:
        console.print(f"\n[red]❌ Tests échoués ({len(failed_tests)}): {', '.join(failed_tests)}[/red]")
    else:
        console.print("\n[green]✅ Tous les tests ont réussi ![/green]")


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Script pour lancer les scénarios")
    parser.add_argument("-s", "--scenario", required=False, help="Nom du scénario")
    parser.add_argument("-a", "--all", required=False, action="store_true", help="Tous les scénarios")
    parser.add_argument("-x", "--exadata", required=False, action="store_true", help="Test Exadata")
    args = parser.parse_args()

    # Vérification des variables d'environnement
    if not check_required_variables():
        return

    work_dir = str(pathlib.Path().resolve())
    
    if scenario := args.scenario:
        is_success = run_scenario(scenario, work_dir, args.exadata)
        
        if is_success:
            console.print(f"\n[green]✅ {scenario}: Succès[/green]")
        else:
            console.print(f"\n[red]❌ {scenario}: Échec[/red]")

    if args.all:
        scenarios_dir = work_dir + "/scenarios/python"
        run_multi_scenarios(scenarios_dir)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interruption par l'utilisateur[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Erreur: {str(e)}[/red]")
```

## 🎨 Améliorations apportées

**✨ Bibliothèque Rich :**

- Console colorée avec emojis
- Barres de chargement avec `Progress` et `SpinnerColumn`
- Panneaux (`Panel`) pour les titres de sections
- Tableau (`Table`) pour les résultats des tests multiples

**🔒 Vérifications ajoutées :**

- Fonction `check_required_variables()` pour valider les variables d’environnement
- Messages d’erreur clairs et colorés

**📝 Code simplifié :**

- Structure claire et lisible
- Messages cohérents avec emojis
- Gestion d’erreurs améliorée

**🎯 Installation de Rich :**

```bash
pip install rich
```