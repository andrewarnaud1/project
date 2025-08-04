"""
yaml_loader.py

Module utilitaire pour charger un fichier YAML en dictionnaire Python,
avec gestion des erreurs de syntaxe YAML, des fichiers manquants,
et des erreurs inattendues.

Fonctions :
-----------
- load_yaml_file(filepath: str) -> dict

Exemples d'utilisation :
------------------------
>>> from yaml_loader import load_yaml_file
>>> config = load_yaml_file('config.yaml')
>>> print(config['app']['name'])

Exceptions :
------------
- ValueError : levée si le fichier est introuvable, invalide ou si une erreur
               de parsing YAML survient.
"""

import yaml


def load_yaml_file(filepath):
    """
    Charge un fichier YAML et retourne son contenu sous forme de dictionnaire.

    :param filepath: Chemin vers le fichier YAML
    :return: Dictionnaire Python
    :raises: ValueError si le YAML est invalide ou le fichier introuvable
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data is not None else {}
    except FileNotFoundError as e:
        raise ValueError(f"Fichier introuvable : '{filepath}'") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Erreur de syntaxe YAML dans '{filepath}': {e}") from e
    except Exception as e:
        raise ValueError(
            f"Erreur inattendue lors du chargement de '{filepath}': {e}"
        ) from e
