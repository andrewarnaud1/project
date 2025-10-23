Améliore le code de ces deux fichiers pour éviter les redondances, maintenir une cohérance et séparer les tâches. Si besoin fait des suggestions de redécoupage de fichier en plusieurs fichier.
L'objectif est de faire en sorte que les fonctions soient claires pour que le code soit lisible et compréhensible par d'autre développeur mais aussi de permettre de ne pas répéter l'appel de fonction et d'avoir un code maintenable.
DAns un premier temps ne génère pas du code pour t'assurer d'avoir compris ma demande. Si me demande n'est pas claire et que tu ne sait pas comment aborder certains points, pose moi des questions pour que je précise ma demande.

Voici le fichier `helpers.py` :

```python
"""
Helpers pour les commandes CLI avec Rich.
"""
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

def print_error(message: str, details: Optional[str] = None) -> None:
    """Affiche un message d’erreur formaté."""
    console.print(f"[bold red][:x:] ERREUR:[/bold red] {message}")
    if details:
        console.print(f"[dim]   {details}[/dim]")

def print_success(message: str) -> None:
    """Affiche un message de succès."""
    console.print(f"[bold green][:white_check_mark:][/bold green] {message}")

def print_warning(message: str, details: Optional[str] = None) -> None:
    """Affiche un avertissement."""
    console.print(f"[bold yellow][:warning:][/bold yellow]  {message}")
    if details:
        console.print(f"[dim]   {details}[/dim]")

def print_info(message: str, details: Optional[str] = None) -> None:
    """Affiche une information."""
    console.print(f"[bold blue][:information_source:][/bold blue]  {message}")
    if details:
        console.print(f"[dim]   {details}[/dim]")

def print_section(title: str) -> None:
    """Affiche un titre de section avec un panel."""
    console.print()
    console.print(Panel(
        Text(title, style="bold cyan", justify="center"),
        border_style="cyan",
        box=box.DOUBLE
        )
    )
    console.print()

def print_status(label: str, value: str, status: str = "info") -> None:
    """
    Affiche un statut formaté (clé-valeur).

    Args:
        label: Le label du statut
        value: La valeur à afficher
        status: Type de statut (info, success, warning, error)
    """
    color_map = {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red"
    }
    color = color_map.get(status, "cyan")
    console.print(f"  [bold]{label}:[/bold] [{color}]{value}[/{color}]")

def check_env_variable(
    var_name: str,
    required: bool = False,
    default_value: Optional[str] = None,
    example_value: List[str] = None,
    description: str = ""
    ) -> Tuple[bool, Optional[str]]:
    """
    Vérifie une variable d’environnement et affiche son état.

    Args:
        var_name: Nom de la variable
        required: Si True, l'absence de la variable est une erreur
        default_value: Valeur par défaut (affichée si la variable n'existe pas)
        description: Description de la variable

    Returns:
        Tuple[bool, Optional[str]]: (est_définie_et_valide, valeur)
    """
    value = os.environ.get(var_name)

    if value is None:
        if required:
            print_error(f"Variable d'environnement '{var_name}' non définie", description)
            if example_value:
                show_usage_example(var_name, example_value)
            return False, None
        elif default_value:
            print_warning(f"'{var_name}' non définie (valeur par défaut utilisée)")
            return True, None
        else:
            print_info(f"'{var_name}' non définie (optionnelle)")
            return True, None
    else:
        print_status(var_name, value, "success")
        return True, value


def check_playwright_installed() -> bool:
    """Vérifie que Playwright et les navigateurs sont installés."""
    try:
        import playwright
        print_success("Playwright est installé")

        # Vérifier si les navigateurs sont installés
        possible_paths = [
            Path.home() / ".cache" / "ms-playwright",
            Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")),
        ]

        browser_found = False
        for browser_path in possible_paths:
            if browser_path.exists():
                firefox_dirs = list(browser_path.glob("firefox-*"))
                if firefox_dirs:
                    browser_found = True
                    print_success(f"Navigateur Firefox trouvé: {firefox_dirs[0].name}")
                    break

        if not browser_found:
            print_warning(
                "Navigateurs Playwright non détectés. Vérifier la variable d'environnement 'PLAYWRIGHT_BROWSERS_PATH'",
                "Installez-les avec: playwright install firefox"
            )
            return True  # Playwright installé, navigateurs manquants

        return True
    except ImportError:
        print_error(
            "Playwright n'est pas installé",
            "Installez avec: pip install playwright && playwright install firefox"
        )
        return False


def show_env_config_help() -> None:
    """Affiche l’aide pour configurer les variables d’environnement."""
    print_section("Configuration des variables d’environnement")

    table = Table(title="Variables d'environnement disponibles", box=box.ROUNDED)
    table.add_column("Variable", style="cyan", no_wrap=True)
    table.add_column("Valeur par défaut", style="yellow")
    table.add_column("Description", style="white")

    table.add_row("URL_API", "http://localhost/", "Base de l'URL de l'API de lecture et d'inscription des données")
    table.add_row("LECTURE", "true", "Lecture des données de l'API")
    table.add_row("INSCRIPTION", "true", "Inscription des données de l'API")
    table.add_row("SIMU_OUTPUT", "/va/simulateur_v6", "Chemin d'enregistrement des rapports JSON, des traces (HAR, ...) et des screenshots")
    table.add_row("PLAYWRIGHT_BROWSERS_PATH", "Chemin créer par Playwright lors de l'installation des navigateur", "Chemin d'installation des navigateurs")
    table.add_row("HEADLESS", "true", "Booléen pour activer la visualisation du scénario")
    table.add_row("NAVIGATEUR", "firefox", "Type de navigateur (firefox, chromium)")
    table.add_row("PROXY", "None", "Proxy")
    table.add_row("CHEMIN_IMAGES_EXADATA", "None", "Chemin vers les images d'un scénario exadata")

    console.print(table)
    console.print()
    console.print("[bold]Configuration permanente:[/bold]")
    console.print("Ajoutez ces lignes à votre [cyan]~/.bashrc[/cyan] ou [cyan]~/.zshrc[/cyan]")
    console.print()


def check_scenario_prerequisites(
    scenario_name: str,
    check_yaml: bool = True,
    check_config: bool = True
) -> bool:
    """
    Vérifie les prérequis pour un scénario.

    ```
    Args:
        scenario_name: Nom du scénario
        check_yaml: Vérifier l'existence du fichier YAML
        check_config: Vérifier l'existence du fichier de configuration

    Returns:
        bool: True si tous les prérequis sont satisfaits
    """
    work_dir = Path.cwd()
    all_ok = True

    print_section(f"Vérification des prérequis: {scenario_name}")

    # Vérifier le fichier YAML
    if check_yaml:
        yaml_file = work_dir / "scenarios" / "yaml" / f"{scenario_name}.yaml"
        if not yaml_file.exists():
            print_error(
                "Fichier YAML de scénario manquant",
                f"Créez le fichier: scenarios/yaml/{scenario_name}.yaml"
            )
            all_ok = False
        else:
            print_success(f"Fichier YAML trouvé: {yaml_file.name}")

    # Vérifier le fichier de configuration
    if check_config:
        config_file = work_dir / "config" / "scenarios" / f"{scenario_name}.conf"
        if not config_file.exists():
            print_error(
                "Fichier de configuration manquant",
                f"Créez le fichier: config/scenarios/{scenario_name}.conf"
            )
            console.print("[dim]   Contenu minimal:[/dim]")
            console.print(f"[cyan]   identifiant: {scenario_name}_001[/cyan]")
            all_ok = False
        else:
            print_success(f"Fichier config trouvé: {config_file.name}")

    return all_ok

def show_usage_example(var: str, examples: List[str]) -> None:
    """Affiche des exemples d’utilisation."""
    print_section("Exemples d’utilisation")
    for example in examples:
        console.print(f"  [cyan]{var}={example}[/cyan]")
        console.print()

def print_test_result(scenario_name: str, success: bool, duration: Optional[float] = None) -> None:
    """
    Affiche le résultat d’un test de façon formatée.

    Args:
        scenario_name: Nom du scénario
        success: True si le test a réussi
        duration: Durée optionnelle du test en secondes
    """
    # todo : Trouver les bons emojis et les ajouter
    status_icon = ":white_check_mark:" if success else ":x:"
    status_text = "SUCCÈS" if success else "ÉCHEC"
    status_color = "green" if success else "red"

    duration_text = f" ({duration:.2f}s)" if duration else ""

    console.print(
        f"[bold]{scenario_name}[/bold]: "
        f"[{status_color}]{status_icon} {status_text}[/{status_color}]"
        f"{duration_text}"
    )

def print_summary_table(results: List[Tuple[str, bool]]) -> None:
    """
    Affiche un tableau récapitulatif des résultats.

    ```
    Args:
        results: Liste de tuples (nom_scenario, succès)
    """
    table = Table(title="Récapitulatif des tests", box=box.ROUNDED)
    table.add_column("Scénario", style="cyan", no_wrap=True)
    table.add_column("Résultat", justify="center")

    success_count = 0
    for scenario, success in results:
        status = "[green][:white_check_mark:] SUCCÈS[/green]" if success else "[red][:x:] ÉCHEC[/red]"
        table.add_row(scenario, status)
        if success:
            success_count += 1

    console.print()
    console.print(table)
    console.print()
    console.print(
        f"[bold]Total:[/bold] {success_count}/{len(results)} tests réussis "
        f"({success_count * 100 // len(results) if results else 0}%)"
    )
```

Voici le fichier `run_scenario` :

```python
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
from rich.progress import Progress, SpinnerColumn, TextColumn

from simulateur.enums import Status
from simulateur.enums import Navigateurs
from simulateur.run_tests_via_yaml import TestAPI
from utils.utils import load_config_files
from utils.yaml_loader import load_yaml_file
from cli.helpers import (
    console,
    print_error,
    print_success,
    print_warning,
    print_info,
    print_section,
    print_test_result,
    print_summary_table,
    check_scenario_prerequisites,
    check_env_variable,
    check_playwright_installed,
    show_env_config_help
)

def init_var_env():
    """
    Récupération des variables d'environnement et mise à jour de l'environnement.
    """
    environnement = {}

    environnement['url_api'] = os.environ.get(
        'URL_API',
        'http://localhost/'
    )

    lecture_env = os.getenv('LECTURE', 'true').lower()
    environnement['lecture'] = lecture_env != 'false'

    inscription_env = os.getenv('INSCRIPTION', 'true').lower()
    environnement['inscription'] = (
        environnement['lecture'] and
        inscription_env != 'false'
    )

    environnement['simu_output'] = os.getenv('SIMU_OUTPUT', "/var/simulateur_v6")

    environnement['playwright_browsers_path'] = os.getenv(
        'PLAYWRIGHT_BROWSERS_PATH'
    )

    headless_env = os.getenv('HEADLESS', 'true').lower()
    environnement['headless'] = headless_env != 'false'

    environnement['navigateur'] = os.getenv("NAVIGATEUR", Navigateurs.FIREFOX.value).lower().strip()

    if 'PROXY' in os.environ:
        environnement['proxy'] = os.getenv('PROXY').strip()
        os.environ['PROXY'] = environnement['proxy']

    if 'CHEMIN_IMAGES_EXADATA' in os.environ:
        environnement['chemin_images_exadata'] = os.getenv('CHEMIN_IMAGES_EXADATA', None).strip()
        os.environ["CHEMIN_IMAGES_EXADATA"] = environnement['chemin_images_exadata']

    os.environ["URL_API"] = environnement['url_api']
    os.environ["LECTURE"] = environnement['lecture']
    os.environ["INSCRIPTION"] = environnement['inscription']
    os.environ["SIMU_OUTPUT"] = environnement['simu_output']
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = environnement['playwright_browsers_path']
    os.environ["HEADLESS"] = environnement['headless']
    os.environ["NAVIGATEUR"] = environnement['navigateur']

    return environnement

def get_scenario_last_execution(identifiant: str, url_api) -> Optional[str]:
    """
    Récupère le statut de la dernière exécution d"un scénario.

    Args:
        identifiant: Identifiant du scénario

    Returns:
        Le statut de la dernière exécution ou None
    """

    url = f"{url_api}/injapi/last_execution/{identifiant}"

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

def get_scenario_info_from_api(scenario_name: str) -> Optional[dict]:
    """
    Récupère les informations d"un scénario depuis l"API.

    Args:
        scenario_name: Nom du scénario

    Returns:
        Dictionnaire avec les infos du scénario ou None
    """

    scenario_id = get_identifiant_from_scenario_name(scenario_name)
    if not scenario_id:
        return None

    url = f"{url_api}/injapi/scenario/{scenario_id}"

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

def get_json_execution(scenario_name: str) -> Optional[dict]:
    """
    Récupère le fichier JSON des résultats d"exécution.

    Args:
        scenario_name: Nom du scénario

    Returns:
        Dictionnaire JSON ou None
    """
    root_dir = None

    if lecture == 'true':
        api_response = get_scenario_info_from_api(scenario_name)
        if api_response is None:
            return None
        root_dir = f"{simu_output}/rapports/{api_response.get('application', {}).get('nom', '')}"
        scenario_name = api_response.get('nom', scenario_name)

    today_report_folder = f'{simu_output if root_dir else root_dir}/{scenario_name}/{datetime.now().date()}'

    try:
        print_info('Voici le chemin vers le rapport', today_report_folder)
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

def post_execution_result_in_isac(scenario_name: str, json_execution: Optional[dict] = None) -> bool:
    """
    Envoie les résultats d"exécution vers ISAC.

    Args:
        scenario_name: Nom du scénario
        json_execution: Données JSON à envoyer (récupérées si None)

    Returns:
        True si l'envoi a réussi
    """
    if json_execution is None:
        json_execution = get_json_execution(scenario_name)

    if json_execution is None:
        print_error("Résultats JSON introuvables")
        return False

    url = f"{url_api}/injapi/scenario/execution"
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

def get_identifiant_from_scenario_name(scenario: str) -> Optional[str]:
    """
    Récupère l"identifiant d"un scénario depuis son fichier de configuration.

    Args:
        scenario: Nom du scénario

    Returns:
        L'identifiant ou None
    """
    config_file = Path.cwd() / "config" / "scenarios" / f"{scenario}.conf"

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

def run_generated_test(work_dir: Path, scenario_name: str, url_api: str) -> bool:
    """
    Exécute un test généré en Python avec pytest.

    Args:
        work_dir: Répertoire de travail
        scenario_name: Nom du scénario

    Returns:
        True si le test a réussi
    """
    file_path = work_dir / "scenarios" / "python" / f"{scenario_name}.py"

    print_info(f"Exécution du test: {file_path.name}")
    result = pytest.main(["-x", "-s", str(file_path)])

    if result != 0:
        scenario_id = get_identifiant_from_scenario_name(scenario_name)
        if not scenario_id:
            print_error("Identifiant du test introuvable dans la configuration")
            return False

        if scenario_id and url_api:
            last_execution_status = get_scenario_last_execution(scenario_id)
            if last_execution_status in [Status.SUCCESS.value, Status.WARNING.value]:
                print_warning("Relance du scénario suite au statut précédent")
                result = pytest.main(["-x", "-s", str(file_path)])
        elif not scenario_id:
            print_error("Identifiant de scénario manquant. Vérification du statut du dernier impossible !")

    return result == 0

def run_exadata_test(work_dir: Path, scenario_name: str) -> bool:
    """
    Exécute un test Exadata.

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

def run_yaml_test(scenario_name: str, scenario_yaml: dict) -> Tuple[bool, Optional[dict]]:
    """
    Exécute un test basé sur un fichier YAML.

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

def run_scenario(scenario_name: str, work_dir: Path, url_api: str, exadata: bool = False) -> bool:
    """
    Exécute un scénario complet.

    Args:
        scenario_name: Nom du scénario
        work_dir: Répertoire de travail
        url_api: base de l'URL des API's (LECTURE et INSCRIPTION)
        exadata: True pour un test Exadata

    Returns:
        True si le scénario a réussi
    """
    print_section(f"Exécution du scénario: {scenario_name}")

    os.environ['SCENARIO'] = scenario_name

    start_time = time.time()
    json_execution = None

    try:
        if exadata:
            is_success = run_exadata_test(work_dir, scenario_name)
        else:
            yaml_file_path = work_dir / "scenarios" / "yaml" / f"{scenario_name}.yaml"

            with open(yaml_file_path) as f:
                scenario_yaml = yaml.safe_load(f)

            scenario_type = scenario_yaml.get('type')

            if scenario_type == 'API':
                is_success, json_execution = run_yaml_test(scenario_name, scenario_yaml)
            else:
                is_success = run_generated_test(work_dir, scenario_name, url_api)

        duration = time.time() - start_time
        print_test_result(scenario_name, is_success, duration)

        post_execution_result_in_isac(scenario_name, json_execution)

        return is_success
    
    except Exception as e:
        print_error(f"Erreur lors de l'exécution du scénario: {str(e)}")
        return False

def run_multi_scenarios(scenarios_dir: Path) -> None:
    """
    Exécute plusieurs scénarios et affiche un récapitulatif.

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

def main():
    """Point d"entrée principal du script."""
    env_vars = init_var_env()

    check_env_variable("SCENARIO", required=True)
    check_env_variable("SIMU_OUTPUT", default_value="/tmp")
    check_env_variable("LECTURE", default_value="true", example_value=["true", "True", "false", "False"])
    check_env_variable("INSCRIPTION", default_value="true", example_value=["true", "True", "false", "False"])
    check_env_variable("NAVIGATEUR", default_value="firefox", example_value=["firefox", "chromium"])
    check_env_variable("HEADLESS", default_value="true", example_value=["true", "True", "false", "False"])

    check_env_variable("URL_API", required=True if env_vars['lecture'] or env_vars['inscription'] else False,
                      description="Nécessaire si LECTURE=true ou INSCRIPTION=true")

    check_playwright_installed()

    parser = argparse.ArgumentParser(
    description="Script pour lancer les scénarios de test",
    formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-s", "--scenario", required=False, help="Nom du scenario")
    parser.add_argument("-a", "--all", required=False, action="store_true",  help="Tous les scenarios")
    parser.add_argument("-x", "--exadata", required=False, action="store_true",  help="Exadata test")


    args = parser.parse_args()
    work_dir = Path.cwd()

    # Exécution d'un scénario unique
    if args.scenario:
        if not check_scenario_prerequisites(args.scenario):
            console.print("\n[red]Prérequis non satisfaits, abandon.[/red]\n")
            return

        is_success = run_scenario(args.scenario, work_dir, args.exadata, env_vars['url_api'])

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
        show_env_config_help()
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interruption par l'utilisateur[/yellow]\n")
    except Exception as e:
        print_error(f"Erreur fatale: {str(e)}")
        console.print_exception()

```
