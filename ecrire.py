"""
Module qui permets d'écrire dans l'interface Guacamole.
"""

from playwright.sync_api import Page
from .cliquer import cliquer


def ecrire(
    image_champ_a_remplir,
    texte,
    page: Page,
):
    """
    Méthode qui permets d'écrire du texte.

    Args:
        image_champ_a_remplir: chemin de l'image du champ à remplir
        texte: texte utilisé pour remplir le champ
        page: page (playwright pour effectuer le screenshot)
    """

    cliquer(image_click=image_champ_a_remplir, page=page)

    page.keyboard.type(texte)
