Parfait ! J’ai bien compris vos objectifs. Voici ma proposition de refactorisation :

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

1. **Variables d’environnement** : Est-ce que l’approche avec le dictionnaire `ENV_VARIABLES` centralisé vous convient ?
1. **Retours de fonctions** : Je propose des retours simples et cohérents :

- Validation : `bool` (True = OK)
- API : `Tuple[bool, Optional[dict]]` (succès, données)
- Tests : `bool` (True = succès)
  
  Cela vous convient ?

1. **Gestion des erreurs** : Les fonctions de validation/vérification affichent les erreurs directement (avec `print_error`) et retournent `False`. L’orchestrateur décide d’arrêter ou continuer. OK ?
1. **Backward compatibility** : Voulez-vous que je garde les mêmes noms de fonctions publiques pour ne pas casser le code existant qui pourrait appeler ces fonctions ?

Est-ce que cette approche correspond à vos attentes ? Dois-je ajuster quelque chose avant de générer le code ?​​​​​​​​​​​​​​​​