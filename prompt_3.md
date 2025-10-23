## Architecture proposée

```
cli/
├── core/
│   ├── __init__.py
│   ├── env_config.py      # Définition centralisée des variables d'env
│   └── paths.py           # Gestion centralisée des chemins
├── services/
│   ├── __init__.py
│   ├── api_client.py      # Tous les appels API
│   └── test_runners.py    # Exécution des différents types de tests
├── ui/
│   ├── __init__.py
│   ├── display.py         # Fonctions d'affichage Rich
│   └── validation.py      # Validation et vérification (env, prérequis)
└── commands/
    ├── __init__.py
    └── run_scenario.py    # Point d'entrée principal (orchestration)
```

## Principes de la refactorisation

### 1. **Séparation claire des responsabilités**

- **core/env_config.py** : Définition unique des variables avec leurs valeurs par défaut, types, descriptions
- **core/paths.py** : Construction des chemins (YAML, config, rapports)
- **services/api_client.py** : Wrapper autour de `requests` avec gestion d’erreur uniforme
- **services/test_runners.py** : Fonctions simples pour exécuter chaque type de test
- **ui/display.py** : Toutes les fonctions d’affichage (actuellement dans helpers.py)
- **ui/validation.py** : Vérification des prérequis et validation de l’environnement
- **commands/run_scenario.py** : Orchestration simple qui appelle les autres modules

### 2. **Gestion des variables d’environnement**

**Approche proposée** : Un dictionnaire de configuration centralisé dans `env_config.py`

```python
# core/env_config.py
ENV_VARIABLES = {
    'URL_API': {
        'default': 'http://localhost/',
        'type': 'str',
        'required_if': ['LECTURE', 'INSCRIPTION'],  # Requis si l'une de ces vars est True
        'description': "Base de l'URL de l'API"
    },
    'LECTURE': {
        'default': True,
        'type': 'bool',
        'description': "Lecture des données de l'API"
    },
    # ... etc
}
```

Utilisation simple :

```python
from cli.core.env_config import get_env_config

env = get_env_config()  # Retourne un dict avec tous les bools convertis
# env['lecture'] est un bool, pas un string
# env['url_api'] est déjà récupéré et disponible
```

### 3. **Gestion des erreurs API uniforme**

```python
# services/api_client.py
def api_get(endpoint, timeout=10):
    """Wrapper GET simple avec gestion d'erreur"""
    # Gestion uniforme des erreurs
    # Retourne (success: bool, data: Optional[dict])
```

### 4. **Fonctions simples et claires**

Chaque fonction fera UNE chose :

- `get_scenario_info()` → appelle l’API
- `validate_scenario_files()` → vérifie les fichiers
- `run_python_test()` → exécute pytest
- etc.

## Points à valider avant de générer le code

1. **Variables d’environnement** : Est-ce que l’approche avec le dictionnaire `ENV_VARIABLES` centralisé vous convient ? Oui
1. **Retours de fonctions** : Je propose des retours simples et cohérents :

- Validation : `bool` (True = OK)
- API : `Tuple[bool, Optional[dict]]` (succès, données)
- Tests : `bool` (True = succès)
  
  Cela vous convient ? Oui

1. **Gestion des erreurs** : Les fonctions de validation/vérification affichent les erreurs directement (avec `print_error`) et retournent `False`. L’orchestrateur décide d’arrêter ou continuer. OK ? Oui
1. **Backward compatibility** : Voulez-vous que je garde les mêmes noms de fonctions publiques pour ne pas casser le code existant qui pourrait appeler ces fonctions ? Non

Est-ce que cette approche correspond à vos attentes ? Dois-je ajuster quelque chose avant de générer le code ?​​​​​​​​​​​​​​​​ Oui cette approche correspond à mes attente

Désormais tu peux générer le code en suivant les instructions que je t'ai données tout au long de notre échange.
Garde bien la structure que j'ai validé.

Voici la structure que j'ai actuellement :

```
cli/
├── encrypt_file.py
├── generate_scenario.py
├── helpers.py
├── __init__.py
└── run_scenario.py
```

Voici le fichier `pyproject.toml` qui se trouve à la racine de mon projet et pas dans le module `cli` :

```
[build-system]
requires = ["setuptools==76.1.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "simulator"
version = "0.0.1"
description = "code métier du simulateur"
requires-python = ">=3.12"
readme = "README.md"
authors = [{name = "DGFiP"}]
dependencies = [
    "pycryptodome==3.23.0",
    "pytest-playwright==0.7.0",
    "pytest-html==4.1.1",
    "pytest-json==0.4.0",
    "psutil==7.0.0",
    "PyYAML==6.0.2",
    "opencv-python==4.12.0.88",
    "Jinja2==3.1.6",
    "jsonschema==4.25.1",
    "cryptography==46.0.2",
    "rich==14.2.0"

]

[project.scripts]
simulateur-encrypt = "cli.encrypt_file:main"
simulateur-generate = "cli.generate_scenario:main"
simulateur-run = "cli.run_scenario:main"

[tool.setuptools.packages.find]
where = ["src"]
```


Voici les autres fichiers du module `cli` :

- `generate_scenario.py` :

```python
#!.env python3

import argparse
import glob
import pathlib

from generateur.generateur import GenerationTest
from utils.yaml_loader import load_yaml_file


def main():
    parser = argparse.ArgumentParser(description="scpript pour generer les scénarios.")
    parser.add_argument("-s", "--scenario", required=False, help="Nom du scenario")
    parser.add_argument("-c", "--commun", required=False, action="store_true", help="Génère tout les étape commune")
    parser.add_argument("-a", "--all", required=False, action="store_true",  help="tout les scenarios")
    args = parser.parse_args()

    work_dir = str(pathlib.Path().resolve())
    scenarios_dir = work_dir + "/scenarios"

    if scenario := args.scenario:
        file_path = f"{scenarios_dir}/yaml/{scenario}.yaml"
        scenario_data = load_yaml_file(file_path)
        generator = GenerationTest()
        generator.creer_scenario_python(scenario_data)

    if args.all:
        scenarios_files = glob.glob(f"{scenarios_dir}/yaml/*.yaml")
        for file_path in scenarios_files:
            scenario_data = load_yaml_file(file_path)
            if scenario_type := scenario_data.get('type'):
                if scenario_type == 'API':
                    continue
            generator = GenerationTest()
            generator.creer_scenario_python(scenario_data)

    if args.commun:
        commun_files = glob.glob(f"{work_dir}/commun/yaml/*.yaml")
        for file_path in commun_files:
            commun_data = load_yaml_file(file_path)
            generator = GenerationTest()
            generator.creer_etapes_communes(commun_data)


if __name__ == "__main__":
    main()
```

- `encrypt_file.py` :
```python
import argparse
import glob
import os
import pathlib

from simulateur.encryptor import Encryptor


def main():
    parser = argparse.ArgumentParser(description="scpript pour encrypter les fichiers de config")
    parser.add_argument("-f", "--file", required=False, help="file path")
    parser.add_argument("-e", "--encrypt", required=False, action="store_true", help="encrypt file")
    parser.add_argument("-d", "--decrypt", required=False, action="store_true", help="decrypt file")
    parser.add_argument("-g", "--genkey", required=False, action="store_true", help="generate key")
    parser.add_argument("-a", "--all", required=False, action="store_true", help="generate key")
    parser.add_argument("-k", "--key", required=False, help="key")

    args = parser.parse_args()

    encryptor = Encryptor()
    if args.genkey:
        key = encryptor.generate_key()
        print(key)
        return
    key = args.key if args.key else os.environ.get('encrypt_key')
    work_dir = str(pathlib.Path().resolve())

    if key is None:
        raise ValueError('key is required')
    files_path = []
    if args.file:
        files_path.append(args.file)

    if args.encrypt:
        if args.all:
            files_path = glob.glob(f"{work_dir}/config/utilisateurs/*.conf")
            for file_path in files_path:
                encryptor.encrypt_file(file_path, key)
    if args.decrypt:
        files_path = glob.glob(f"{work_dir}/config/utilisateurs/*.encrypted")
        for file_path in files_path:
            encryptor.decrypt_file(file_path, key)

if __name__ == "__main__":
    main()
```
