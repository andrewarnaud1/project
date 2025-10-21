“””
Helpers pour les commandes CLI avec Rich.
“””
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# Console globale pour toutes les sorties

console = Console()

def print_error(message: str, details: Optional[str] = None) -> None:
“”“Affiche un message d’erreur formaté.”””
console.print(f”[bold red]❌ ERREUR:[/bold red] {message}”)
if details:
console.print(f”[dim]   {details}[/dim]”)

def print_success(message: str) -> None:
“”“Affiche un message de succès.”””
console.print(f”[bold green]✓[/bold green] {message}”)

def print_warning(message: str, details: Optional[str] = None) -> None:
“”“Affiche un avertissement.”””
console.print(f”[bold yellow]⚠[/bold yellow]  {message}”)
if details:
console.print(f”[dim]   {details}[/dim]”)

def print_info(message: str, details: Optional[str] = None) -> None:
“”“Affiche une information.”””
console.print(f”[bold blue]ℹ[/bold blue]  {message}”)
if details:
console.print(f”[dim]   {details}[/dim]”)

def print_section(title: str) -> None:
“”“Affiche un titre de section avec un panel.”””
console.print()
console.print(Panel(
Text(title, style=“bold cyan”, justify=“center”),
border_style=“cyan”,
box=box.DOUBLE
))
console.print()

def print_status(label: str, value: str, status: str = “info”) -> None:
“””
Affiche un statut formaté (clé-valeur).

```
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
```

def check_env_variable(
var_name: str,
required: bool = False,
recommended_value: Optional[str] = None,
description: str = “”
) -> Tuple[bool, Optional[str]]:
“””
Vérifie une variable d’environnement et affiche son état.

```
Args:
    var_name: Nom de la variable
    required: Si True, l'absence de la variable est une erreur
    recommended_value: Valeur recommandée (affichée si la variable n'existe pas)
    description: Description de la variable

Returns:
    Tuple[bool, Optional[str]]: (est_définie_et_valide, valeur)
"""
value = os.environ.get(var_name)

if value is None:
    if required:
        print_error(f"Variable d'environnement '{var_name}' non définie", description)
        if recommended_value:
            console.print(f"[dim]   Valeur recommandée:[/dim] [cyan]{recommended_value}[/cyan]")
        return False, None
    elif recommended_value:
        print_warning(f"'{var_name}' non définie (valeur par défaut utilisée)")
        return True, None
    else:
        print_info(f"'{var_name}' non définie (optionnelle)")
        return True, None
else:
    print_status(var_name, value, "success")
    return True, value
```

def check_file_exists(file_path: str, description: str = “”) -> bool:
“”“Vérifie qu’un fichier existe.”””
path = Path(file_path)
if not path.exists():
print_error(f”Fichier introuvable: {file_path}”, description)
return False
print_success(f”Fichier trouvé: {file_path}”)
return True

def check_directory_exists(dir_path: str, description: str = “”, create: bool = False) -> bool:
“”“Vérifie qu’un répertoire existe (peut le créer si create=True).”””
path = Path(dir_path)
if not path.exists():
if create:
print_warning(f”Répertoire ‘{dir_path}’ introuvable, création en cours…”)
path.mkdir(parents=True, exist_ok=True)
print_success(f”Répertoire créé: {dir_path}”)
return True
else:
print_error(f”Répertoire introuvable: {dir_path}”, description)
return False
print_success(f”Répertoire trouvé: {dir_path}”)
return True

def check_playwright_installed() -> bool:
“”“Vérifie que Playwright et les navigateurs sont installés.”””
try:
import playwright
print_success(“Playwright est installé”)

```
    # Vérifier si les navigateurs sont installés
    possible_paths = [
        Path.home() / "Library" / "Caches" / "ms-playwright",  # macOS
        Path.home() / ".cache" / "ms-playwright",  # Linux
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
            "Navigateurs Playwright non détectés",
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
```

def show_env_config_help() -> None:
“”“Affiche l’aide pour configurer les variables d’environnement.”””
print_section(“Configuration des variables d’environnement”)

```
table = Table(title="Variables d'environnement disponibles", box=box.ROUNDED)
table.add_column("Variable", style="cyan", no_wrap=True)
table.add_column("Valeur", style="yellow")
table.add_column("Description", style="white")

table.add_row("LECTURE", "false", "Désactive la lecture depuis l'API")
table.add_row("INSCRIPTION", "false", "Désactive l'enregistrement dans l'API")
table.add_row("NAVIGATEUR", "firefox", "Type de navigateur (firefox, chromium)")
table.add_row("HEADLESS", "true", "Mode headless (true/false)")
table.add_row("URL_API", "http://...", "URL de l'API (si LECTURE=true)")

console.print(table)
console.print()
console.print("[bold]Configuration permanente:[/bold]")
console.print("Ajoutez ces lignes à votre [cyan]~/.bashrc[/cyan] ou [cyan]~/.zshrc[/cyan]")
console.print()
```

def check_scenario_prerequisites(
scenario_name: str,
check_yaml: bool = True,
check_config: bool = True
) -> bool:
“””
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
```

def show_usage_example(command: str, examples: List[str]) -> None:
“”“Affiche des exemples d’utilisation.”””
print_section(“Exemples d’utilisation”)
for example in examples:
console.print(f”  [cyan]{command} {example}[/cyan]”)
console.print()

def exit_with_error(message: str, show_help: bool = True) -> None:
“”“Affiche une erreur et quitte le programme.”””
console.print()
print_error(message)
if show_help:
console.print()
console.print(“Pour plus d’aide: [cyan]–help[/cyan]”)
console.print()
sys.exit(1)

def print_test_result(scenario_name: str, success: bool, duration: Optional[float] = None) -> None:
“””
Affiche le résultat d’un test de façon formatée.

```
Args:
    scenario_name: Nom du scénario
    success: True si le test a réussi
    duration: Durée optionnelle du test en secondes
"""
status_icon = "✅" if success else "❌"
status_text = "SUCCÈS" if success else "ÉCHEC"
status_color = "green" if success else "red"

duration_text = f" ({duration:.2f}s)" if duration else ""

console.print(
    f"[bold]{scenario_name}[/bold]: "
    f"[{status_color}]{status_icon} {status_text}[/{status_color}]"
    f"{duration_text}"
)
```

def print_summary_table(results: List[Tuple[str, bool]]) -> None:
“””
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
    status = "[green]✅ SUCCÈS[/green]" if success else "[red]❌ ÉCHEC[/red]"
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