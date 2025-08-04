"""
Module de conversion de chaine de caractère en booléen.
"""

from .constantes import ConstantesSimulateur


def convertir_booleen(valeur: str, nom_variable: str) -> bool:
    """
    Convertit une chaîne en booléen selon les constantes définies.

    Args:
        valeur: Valeur à convertir
        nom_variable: Nom de la variable (pour les erreurs)

    Returns:
        bool: Valeur booléenne

    Raises:
        ValueError: si valeur invalide
    """
    valeur_lower = valeur.lower().strip()

    if valeur_lower in ConstantesSimulateur.VALEURS_BOOLEAN_TRUE:
        return True
    elif valeur_lower in ConstantesSimulateur.VALEURS_BOOLEAN_FALSE:
        return False
    else:
        raise ValueError(
            f"Valeur booléenne invalide pour {nom_variable} : '{valeur}'. "
            f"Valeurs autorisées : {', '.join(ConstantesSimulateur.VALEURS_BOOLEAN_VALIDES)}",
        )
