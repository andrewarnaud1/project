Dans un premier temps, je veux modifer les méthodes de mon fichiers `helpers.py` pour utiliser la bibliothèque rich de Python afin d'enrichier les output de mon terminal.
Une fois le fichier `helpers.py` modifier il faut utiliser les méthodes du fichier dans le fichier `run_scenario.py`.

Optimiser le code et les méthodes pour faciliter leurs compréhension et leur utilisation.

Voici le fichier `helpers.py` :

```python
"""
Helpers pour les commandes CLI.
"""
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple


# Couleurs pour les messages (compatibles Linux/Mac)
class Colors:
    """Codes couleurs ANSI pour les messages."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'


def print_error(message: str) -> None:
    """Affiche un message d'erreur en rouge."""
    print(f"{Colors.RED}❌ ERREUR:{Colors.RESET} {message}")


def print_success(message: str) -> None:
    """Affiche un message de succès en vert."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")


def print_warning(message: str) -> None:
    """Affiche un avertissement en jaune."""
    print(f"{Colors.YELLOW}⚠{Colors.RESET}  {message}")


def print_info(message: str) -> None:
    """Affiche une information en bleu."""
    print(f"{Colors.BLUE}ℹ{Colors.RESET}  {message}")


def print_section(title: str) -> None:
    """Affiche un titre de section."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══ {title} ═══{Colors.RESET}\n")


def check_env_variable(
    var_name: str,
    required: bool = False,
    recommended_value: Optional[str] = None,
    description: str = ""
) -> Tuple[bool, Optional[str]]:
    """
    Vérifie une variable d'environnement.

    Returns:
        Tuple[bool, Optional[str]]: (est_définie, valeur)
    """
    value = os.environ.get(var_name)

    if value is None:
        if required:
            print_error(f"Variable d'environnement {var_name} non définie")
            if description:
                print(f"   {description}")
            if recommended_value:
                print(f"   Valeur recommandée : {Colors.CYAN}{recommended_value}{Colors.RESET}")
            return False, None
        elif recommended_value:
            print_warning(f"{var_name} non définie (valeur par défaut utilisée)")
            return True, None
    else:
        print_info(f"{var_name}={Colors.CYAN}{value}{Colors.RESET}")
        return True, value

    return True, value


def check_file_exists(file_path: str, description: str = "") -> bool:
    """Vérifie qu'un fichier existe."""
    path = Path(file_path)
    if not path.exists():
        print_error(f"Fichier introuvable : {file_path}")
        if description:
            print(f"   {description}")
        return False
    return True


def check_directory_exists(dir_path: str, description: str = "", create: bool = False) -> bool:
    """Vérifie qu'un répertoire existe (peut le créer si create=True)."""
    path = Path(dir_path)
    if not path.exists():
        if create:
            print_warning(f"Répertoire {dir_path} introuvable, création...")
            path.mkdir(parents=True, exist_ok=True)
            print_success(f"Répertoire créé : {dir_path}")
            return True
        else:
            print_error(f"Répertoire introuvable : {dir_path}")
            if description:
                print(f"   {description}")
            return False
    return True


def check_playwright_installed() -> bool:
    """Vérifie que Playwright et les navigateurs sont installés."""
    try:
        import playwright
        print_success("Playwright installé")

        # Vérifier si les navigateurs sont installés
        from pathlib import Path
        import os

        # Chemins où Playwright installe les navigateurs
        possible_paths = [
            Path.home() / "Library" / "Caches" / "ms-playwright",  # macOS
            Path.home() / ".cache" / "ms-playwright",  # Linux
            Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")),  # Custom
        ]

        browser_found = False
        for browser_path in possible_paths:
            if browser_path.exists():
                firefox_dirs = list(browser_path.glob("firefox-*"))
                if firefox_dirs:
                    browser_found = True
                    print_success(f"Navigateur Firefox trouvé : {firefox_dirs[0]}")
                    break

        if not browser_found:
            print_warning("Navigateurs Playwright non détectés")
            print(f"   Installer avec : {Colors.CYAN}playwright install firefox{Colors.RESET}")
            return True  # Playwright est installé, juste les browsers qui manquent

        return True
    except ImportError:
        print_error("Playwright n'est pas installé")
        print(f"   Installer avec : {Colors.CYAN}pip install playwright{Colors.RESET}")
        print(f"   Puis installer les navigateurs : {Colors.CYAN}playwright install firefox{Colors.RESET}")
        return False


def show_env_config_help() -> None:
    """Affiche l'aide pour configurer les variables d'environnement."""
    print_section("Configuration des variables d'environnement")

    print(f"{Colors.BOLD}Pour le développement local :{Colors.RESET}")
    print(f"  {Colors.CYAN}export LECTURE=false{Colors.RESET}       # Désactive la lecture depuis l'API")
    print(f"  {Colors.CYAN}export INSCRIPTION=false{Colors.RESET}   # Désactive l'enregistrement dans l'API")
    print()

    print(f"{Colors.BOLD}Variables optionnelles :{Colors.RESET}")
    print(f"  {Colors.CYAN}export NAVIGATEUR=firefox{Colors.RESET}  # Type de navigateur (firefox, chromium)")
    print(f"  {Colors.CYAN}export HEADLESS=true{Colors.RESET}       # Mode headless (true/false)")
    print(f"  {Colors.CYAN}export URL_API=http://...</ {Colors.RESET}      # URL de l'API (si LECTURE=true)")
    print()

    print(f"{Colors.BOLD}Pour configurer de façon permanente :{Colors.RESET}")
    print(f"  Ajoutez ces lignes à votre {Colors.CYAN}~/.bashrc{Colors.RESET} ou {Colors.CYAN}~/.zshrc{Colors.RESET}")
    print()


def check_scenario_prerequisites(scenario_name: str, check_yaml: bool = True, check_config: bool = True) -> bool:
    """
    Vérifie les prérequis pour un scénario.

    Args:
        scenario_name: Nom du scénario
        check_yaml: Vérifier que le fichier YAML existe
        check_config: Vérifier que le fichier de config existe

    Returns:
        bool: True si tous les prérequis sont OK
    """
    work_dir = Path.cwd()
    all_ok = True

    # Vérifier le fichier YAML
    if check_yaml:
        yaml_file = work_dir / "scenarios" / "yaml" / f"{scenario_name}.yaml"
        if not check_file_exists(str(yaml_file), "Fichier de définition du scénario"):
            print(f"   Créez le fichier : {Colors.CYAN}scenarios/yaml/{scenario_name}.yaml{Colors.RESET}")
            all_ok = False

    # Vérifier le fichier de configuration
    if check_config:
        config_file = work_dir / "config" / "scenarios" / f"{scenario_name}.conf"
        if not check_file_exists(str(config_file), "Fichier de configuration du scénario"):
            print(f"   Créez le fichier : {Colors.CYAN}config/scenarios/{scenario_name}.conf{Colors.RESET}")
            print(f"   Contenu minimal :")
            print(f"   {Colors.CYAN}identifiant: {scenario_name}_001{Colors.RESET}")
            all_ok = False

    return all_ok


def show_usage_example(command: str, examples: List[str]) -> None:
    """Affiche des exemples d'utilisation."""
    print_section("Exemples d'utilisation")
    for example in examples:
        print(f"  {Colors.CYAN}{command} {example}{Colors.RESET}")
    print()


def exit_with_error(message: str, show_help: bool = True) -> None:
    """Affiche une erreur et quitte le programme."""
    print()
    print_error(message)
    if show_help:
        print()
        print(f"Pour plus d'aide : {Colors.CYAN}--help{Colors.RESET}")
    print()
    sys.exit(1)

```

Voici le fichier `run_scenario.py` :

```python
#!.env python3

import argparse
from datetime import datetime
import glob
import os
import pathlib
import pytest
import requests
import yaml
from simulateur.enums import Status
from simulateur.run_tests_via_yaml import TestAPI
from utils.utils import load_config_files
from utils.yaml_loader import load_yaml_file

URL_API = os.environ.get('URL_API', None)

def get_scenario_last_execution(identifiant: str):
    if not identifiant:
        return None
    if not URL_API:
        raise KeyError('url_api non défini')
    url = f"{URL_API}/injapi/last_execution/{identifiant}"
    try:
        response  = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None

        response_json = response.json()
        execution =  response_json.get('execution')
        if not execution:
            return None
        return execution.get('status', None)
    except Exception:
        print('impossible de récuperer le status de la dérnière execution du scenario')
        return None


def get_scenario_info_from_api(scenario_name):
    scenario_id = get_indentifiant_from_scenario_name(scenario_name)
    url = f"{URL_API}injapi/scenario/{scenario_id}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()
    return None


def get_json_execution(scenario_name: str):
    root_dir =  os.environ.get('SIMU_OUTPUT', '/tmp')
    lecture = os.environ.get('LECTURE', None).lower()
    if lecture == 'true':
        api_response = get_scenario_info_from_api(scenario_name)
        if api_response is None:
            return None
        root_dir = f"{root_dir}/{api_response.get('application').get('nom')}"
        scenario_name = api_response.get('nom')

    today_report_folder = f'{root_dir}/{scenario_name}/{datetime.now().date()}'
    last_report_folder = max(pathlib.Path(today_report_folder).glob('*/'), key=os.path.getmtime)
    json_path = f"{str(last_report_folder)}/scenario.json"
    return load_yaml_file(json_path)


def post_execution_result_in_isac(scenario_name: str, json_execution:dict = None):
    inscription = os.environ.get('INSCRIPTION', None).lower()

    if inscription == 'true':
        if not URL_API:
            print("la variable url_api n'est pas défini")
            return

        url = f"{URL_API}/injapi/scenario/execution"
        if json_execution is None:
            json_execution = get_json_execution(scenario_name)
        if json_execution is None:
            print("le fichier json des resultats de scenarion est introuvable")
            return

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/plain",
        }

        response = requests.post(url, headers=headers, timeout=10, json=json_execution)
        if response.status_code != 201:
            print("impossible de sauvgarder le resultat du scenarion dans isac")
            return
        print("sauvgarder le resultat du scenarion dans isac")


def get_indentifiant_from_scenario_name(scenario: str):
    work_dir = str(pathlib.Path().resolve())
    config_file = f"{work_dir}/config/scenarios/{scenario}.conf"
    configuration = load_yaml_file(config_file)
    return configuration.get('identifiant', None)

def run_generated_test(work_dir: str, scenario_name :str):
    file_path = f"{work_dir}/scenarios/python/{scenario_name}.py"
    result = pytest.main(["-x", "-s", file_path])

    if result != 0:
        scenario_id = get_indentifiant_from_scenario_name(scenario_name)
        if not scenario_id:
            raise KeyError("l'identifiant du test dans le fichier de configuration est introuvable!")
        last_execution_status = get_scenario_last_execution(scenario_id)
        if last_execution_status is None:
            return False
        if last_execution_status in [Status.SUCCESS.value, Status.WARNING.value]:
            print("re-lancer le scenario ")
            result = pytest.main(["-x", "-s", file_path])
            if result != 0:
                return False
    return result == 0

def run_exadata_test(work_dir: str, scenario_name: str):
    os.environ['chemin_images_exadata'] = f"{work_dir}/scenarios_exadata/images/{scenario_name}"
    file_path = f"{work_dir}/scenarios_exadata/{scenario_name}.py"
    result = pytest.main(["-x", "-s", file_path])
    return result == 0

def run_yaml_test(scenario_name: str, scenario_yaml : dict):
    scenario_config = load_config_files(scenario_name)
    test_api_runner = TestAPI(scenario_yaml, scenario_config)
    return test_api_runner.run()

def run_scenario(scenario_name: str, work_dir: str, exadata: bool = None):
    is_success = False
    json_execution = None
    scenario_yaml = None

    os.environ['SCENARIO'] = scenario_name

    if exadata:
        is_success = run_exadata_test(work_dir, scenario_name)

    else:
        yaml_file_path = f"scenarios/yaml/{scenario_name}.yaml"
        with open(yaml_file_path) as f:
            scenario_yaml = yaml.safe_load(f)

        if scenario_type := scenario_yaml.get('type'):
            if scenario_type == 'API': # todo we will add DNS, TELNET SMTP ...etc
                is_success, json_execution  = run_yaml_test(scenario_name, scenario_yaml)
        else:
            is_success = run_generated_test(work_dir, scenario_name)

    try:
        post_execution_result_in_isac(scenario_name, json_execution)
    except Exception as e:
        raise TimeoutError('impossible de sauvgarder le resultat dans ISAC!', str(e))
    return is_success

def run_multi_scenarios(scenarios_dir: str):
    failed_tests = []
    scenarios_files = glob.glob(f"{scenarios_dir}/*.py")
    for file_path in scenarios_files:
        scenario = file_path.split('/')[-1].split('.')[0]
        os.environ['SCENARIO'] = scenario
        result = pytest.main(["-x", "-s", file_path])
        if result == 0:
            print(f"{scenario} test: OK ✅")
        else:
            failed_tests.append(scenario)
            print(f"{scenario} test: KO ❌")
    print(f"failed tests {len(failed_tests)}", failed_tests)

def main():
    parser = argparse.ArgumentParser(description="scpript pour lancer les scénarios.")
    parser.add_argument("-s", "--scenario", required=False, help="Nom du scenario")
    parser.add_argument("-a", "--all", required=False, action="store_true",  help="tout les scenarios")
    parser.add_argument("-x", "--exadata", required=False, action="store_true",  help="exadata test")
    args = parser.parse_args()

    work_dir = str(pathlib.Path().resolve())
    if scenario := args.scenario:
        is_success = run_scenario(scenario, work_dir, args.exadata)
        if is_success:
            print(f"{scenario} test: OK ✅")
        else:
            print(f"{scenario} test: KO ❌")

    if args.all: # pour tester en local
        scenarios_dir = work_dir + "/scenarios/python"
        run_multi_scenarios(scenarios_dir)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("erreur lors de l'execution du scenarion", str(e))

```
