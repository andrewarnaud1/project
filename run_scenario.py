#!/usr/bin/env python3

import argparse
import glob
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import pytest
import requests
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from simulateur.enums import Status
from simulateur.run_tests_via_yaml import TestAPI
from utils.utils import load_config_files
from utils.yaml_loader import load_yaml_file
from helpers import (
console,
print_error,
print_success,
print_warning,
print_info,
print_section,
print_test_result,
print_summary_table,
check_scenario_prerequisites
)

URL_API = os.environ.get(‘URL_API’)

def get_scenario_last_execution(identifiant: str) -> Optional[str]:
“””
Récupère le statut de la dernière exécution d’un scénario.

```
Args:
    identifiant: Identifiant du scénario
    
Returns:
    Le statut de la dernière exécution ou None
"""
if not identifiant:
    print_warning("Identifiant de scénario manquant")
    return None

if not URL_API:
    print_error("Variable URL_API non définie")
    return None

url = f"{URL_API}/injapi/last_execution/{identifiant}"

try:
    with console.status(f"[bold cyan]Récupération du statut pour {identifiant}..."):
        response = requests.get(url, timeout=10)
    
    if response.status_code != 200:
        print_warning(f"Statut HTTP {response.status_code} pour {identifiant}")
        return None

    response_json = response.json()
    execution = response_json.get('execution')
    
    if not execution:
        print_warning("Aucune exécution trouvée")
        return None
    
    status = execution.get('status')
    print_info(f"Dernier statut: {status}")
    return status
    
except requests.exceptions.Timeout:
    print_error("Timeout lors de la récupération du statut")
    return None
except Exception as e:
    print_error(f"Erreur lors de la récupération du statut: {str(e)}")
    return None
```

def get_scenario_info_from_api(scenario_name: str) -> Optional[dict]:
“””
Récupère les informations d’un scénario depuis l’API.

```
Args:
    scenario_name: Nom du scénario
    
Returns:
    Dictionnaire avec les infos du scénario ou None
"""
if not URL_API:
    print_error("Variable URL_API non définie")
    return None

scenario_id = get_identifiant_from_scenario_name(scenario_name)
if not scenario_id:
    return None

url = f"{URL_API}/injapi/scenario/{scenario_id}"

try:
    with console.status(f"[bold cyan]Récupération des infos pour {scenario_name}..."):
        response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        print_success("Informations récupérées depuis l'API")
        return response.json()
    
    print_warning(f"Scénario non trouvé dans l'API (statut {response.status_code})")
    return None
    
except Exception as e:
    print_error(f"Erreur API: {str(e)}")
    return None
```

def get_json_execution(scenario_name: str) -> Optional[dict]:
“””
Récupère le fichier JSON des résultats d’exécution.

```
Args:
    scenario_name: Nom du scénario
    
Returns:
    Dictionnaire JSON ou None
"""
root_dir = os.environ.get('SIMU_OUTPUT', '/tmp')
lecture = os.environ.get('LECTURE', '').lower()

if lecture == 'true':
    api_response = get_scenario_info_from_api(scenario_name)
    if api_response is None:
        return None
    root_dir = f"{root_dir}/{api_response.get('application', {}).get('nom', '')}"
    scenario_name = api_response.get('nom', scenario_name)

today_report_folder = f'{root_dir}/{scenario_name}/{datetime.now().date()}'

try:
    last_report_folder = max(
        Path(today_report_folder).glob('*/'),
        key=os.path.getmtime
    )
    json_path = last_report_folder / "scenario.json"
    
    if not json_path.exists():
        print_error(f"Fichier JSON introuvable: {json_path}")
        return None
    
    print_success(f"Fichier JSON trouvé: {json_path}")
    return load_yaml_file(str(json_path))
    
except (ValueError, FileNotFoundError) as e:
    print_error(f"Erreur lors de la lecture du JSON: {str(e)}")
    return None
```

def post_execution_result_in_isac(scenario_name: str, json_execution: Optional[dict] = None) -> bool:
“””
Envoie les résultats d’exécution vers ISAC.

```
Args:
    scenario_name: Nom du scénario
    json_execution: Données JSON à envoyer (récupérées si None)
    
Returns:
    True si l'envoi a réussi
"""
inscription = os.environ.get('INSCRIPTION', '').lower()

if inscription != 'true':
    print_info("Inscription désactivée (INSCRIPTION != true)")
    return True

if not URL_API:
    print_error("Variable URL_API non définie")
    return False

if json_execution is None:
    json_execution = get_json_execution(scenario_name)

if json_execution is None:
    print_error("Résultats JSON introuvables")
    return False

url = f"{URL_API}/injapi/scenario/execution"
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Accept": "text/plain",
}

try:
    with console.status("[bold cyan]Envoi des résultats vers ISAC..."):
        response = requests.post(url, headers=headers, timeout=10, json=json_execution)
    
    if response.status_code == 201:
        print_success("Résultats sauvegardés dans ISAC")
        return True
    else:
        print_error(f"Échec de sauvegarde dans ISAC (statut {response.status_code})")
        return False
        
except requests.exceptions.Timeout:
    print_error("Timeout lors de l'envoi vers ISAC")
    return False
except Exception as e:
    print_error(f"Erreur lors de l'envoi vers ISAC: {str(e)}")
    return False
```

def get_identifiant_from_scenario_name(scenario: str) -> Optional[str]:
“””
Récupère l’identifiant d’un scénario depuis son fichier de configuration.

```
Args:
    scenario: Nom du scénario
    
Returns:
    L'identifiant ou None
"""
config_file = Path.cwd() / "config" / "scenarios" / f"{scenario}.conf"

if not config_file.exists():
    print_error(f"Fichier de configuration introuvable: {config_file}")
    return None

try:
    configuration = load_yaml_file(str(config_file))
    identifiant = configuration.get('identifiant')
    
    if identifiant:
        print_info(f"Identifiant: {identifiant}")
    else:
        print_warning("Identifiant manquant dans la configuration")
    
    return identifiant
    
except Exception as e:
    print_error(f"Erreur de lecture de la configuration: {str(e)}")
    return None
```

def run_generated_test(work_dir: Path, scenario_name: str) -> bool:
“””
Exécute un test généré en Python avec pytest.

```
Args:
    work_dir: Répertoire de travail
    scenario_name: Nom du scénario
    
Returns:
    True si le test a réussi
"""
file_path = work_dir / "scenarios" / "python" / f"{scenario_name}.py"

if not file_path.exists():
    print_error(f"Fichier de test introuvable: {file_path}")
    return False

print_info(f"Exécution du test: {file_path.name}")
result = pytest.main(["-x", "-s", str(file_path)])

if result != 0:
    scenario_id = get_identifiant_from_scenario_name(scenario_name)
    if not scenario_id:
        print_error("Identifiant du test introuvable dans la configuration")
        return False
    
    last_execution_status = get_scenario_last_execution(scenario_id)
    
    if last_execution_status in [Status.SUCCESS.value, Status.WARNING.value]:
        print_warning("Relance du scénario suite au statut précédent")
        result = pytest.main(["-x", "-s", str(file_path)])

return result == 0
```

def run_exadata_test(work_dir: Path, scenario_name: str) -> bool:
“””
Exécute un test Exadata.

```
Args:
    work_dir: Répertoire de travail
    scenario_name: Nom du scénario
    
Returns:
    True si le test a réussi
"""
images_dir = work_dir / "scenarios_exadata" / "images" / scenario_name
os.environ['chemin_images_exadata'] = str(images_dir)

file_path = work_dir / "scenarios_exadata" / f"{scenario_name}.py"

if not file_path.exists():
    print_error(f"Test Exadata introuvable: {file_path}")
    return False

print_info(f"Exécution du test Exadata: {file_path.name}")
result = pytest.main(["-x", "-s", str(file_path)])

return result == 0
```

def run_yaml_test(scenario_name: str, scenario_yaml: dict) -> Tuple[bool, Optional[dict]]:
“””
Exécute un test basé sur un fichier YAML.

```
Args:
    scenario_name: Nom du scénario
    scenario_yaml: Contenu du fichier YAML
    
Returns:
    Tuple (succès, json_execution)
"""
print_info("Exécution du test API basé sur YAML")

scenario_config = load_config_files(scenario_name)
test_api_runner = TestAPI(scenario_yaml, scenario_config)

return test_api_runner.run()
```

def run_scenario(scenario_name: str, work_dir: Path, exadata: bool = False) -> bool:
“””
Exécute un scénario complet.

```
Args:
    scenario_name: Nom du scénario
    work_dir: Répertoire de travail
    exadata: True pour un test Exadata
    
Returns:
    True si le scénario a réussi
"""
print_section(f"Exécution du scénario: {scenario_name}")

os.environ['SCENARIO'] = scenario_name

start_time = time.time()
is_success = False
json_execution = None

try:
    if exadata:
        is_success = run_exadata_test(work_dir, scenario_name)
    else:
        yaml_file_path = work_dir / "scenarios" / "yaml" / f"{scenario_name}.yaml"
        
        if not yaml_file_path.exists():
            print_error(f"Fichier YAML introuvable: {yaml_file_path}")
            return False
        
        with open(yaml_file_path) as f:
            scenario_yaml = yaml.safe_load(f)

        scenario_type = scenario_yaml.get('type')
        
        if scenario_type == 'API':
            is_success, json_execution = run_yaml_test(scenario_name, scenario_yaml)
        else:
            is_success = run_generated_test(work_dir, scenario_name)

    duration = time.time() - start_time
    print_test_result(scenario_name, is_success, duration)
    
    # Envoi des résultats vers ISAC
    post_execution_result_in_isac(scenario_name, json_execution)
    
    return is_success
    
except Exception as e:
    print_error(f"Erreur lors de l'exécution du scénario: {str(e)}")
    return False
```

def run_multi_scenarios(scenarios_dir: Path) -> None:
“””
Exécute plusieurs scénarios et affiche un récapitulatif.

```
Args:
    scenarios_dir: Répertoire contenant les scénarios
"""
print_section("Exécution de tous les scénarios")

scenarios_files = list(scenarios_dir.glob("*.py"))

if not scenarios_files:
    print_warning(f"Aucun scénario trouvé dans {scenarios_dir}")
    return

print_info(f"{len(scenarios_files)} scénario(s) trouvé(s)")

results = []

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    console=console
) as progress:
    task = progress.add_task("Exécution des tests...", total=len(scenarios_files))
    
    for file_path in scenarios_files:
        scenario = file_path.stem
        os.environ['SCENARIO'] = scenario
        
        progress.update(task, description=f"Test: {scenario}")
        
        result = pytest.main(["-x", "-s", str(file_path)])
        success = result == 0
        
        results.append((scenario, success))
        print_test_result(scenario, success)
        
        progress.advance(task)

print_summary_table(results)
```

def main():
“”“Point d’entrée principal du script.”””
parser = argparse.ArgumentParser(
description=“Script pour lancer les scénarios de test”,
formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument(
“-s”, “–scenario”,
help=“Nom du scénario à exécuter”
)
parser.add_argument(
“-a”, “–all”,
action=“store_true”,
help=“Exécuter tous les scénarios”
)
parser.add_argument(
“-x”, “–exadata”,
action=“store_true”,
help=“Mode test Exadata”
)

```
args = parser.parse_args()
work_dir = Path.cwd()

# Exécution d'un scénario unique
if args.scenario:
    if not check_scenario_prerequisites(args.scenario):
        console.print("\n[red]Prérequis non satisfaits, abandon.[/red]\n")
        return
    
    is_success = run_scenario(args.scenario, work_dir, args.exadata)
    
    if not is_success:
        console.print("\n[red bold]Le scénario a échoué[/red bold]\n")
        exit(1)

# Exécution de tous les scénarios
elif args.all:
    scenarios_dir = work_dir / "scenarios" / "python"
    
    if not scenarios_dir.exists():
        print_error(f"Répertoire de scénarios introuvable: {scenarios_dir}")
        return
    
    run_multi_scenarios(scenarios_dir)

else:
    parser.print_help()
```

if **name** == “**main**”:
try:
main()
except KeyboardInterrupt:
console.print(”\n[yellow]Interruption par l’utilisateur[/yellow]\n”)
except Exception as e:
print_error(f”Erreur fatale: {str(e)}”)
console.print_exception()