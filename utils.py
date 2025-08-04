"""
utils.py

Outils divers pour le projet.

Fonctions :
-----------
- methode_contexte() -> str

Exemples d'utilisation :
------------------------
>>> from src.utils import methode_contexte

>>> methode_contexte = methode_contexte()
>>> print(methode_contexte)

Exceptions :
------------
"""

import inspect


def contexte_actuel(objet_self=None):
    """
    Retourne le contexte de la méthode en cours d'exécution.

    :param objet_self: Optionnel, l'objet self de la méthode en cours d'exécution
    :return: str
    """

    frame = inspect.currentframe().f_back
    nom_fonction = frame.f_code.co_name
    if objet_self:
        return f"{objet_self.__class__.__name__}.{nom_fonction}"
    return nom_fonction
