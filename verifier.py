"""
Module d'action de vérification.
"""

from time import sleep
from playwright.sync_api import Page
from .trouver_coordonnees_image import trouver_coordonnees_image


def verifier(
    image_a_verifier,
    page: Page,
    obligatoire=True,
    cpt_duree=150
):
    """
    Permets de verifier qu'un élément existe sur la page à partir 
    du screenshot de l'écran et d'un screenshot de l'élément sur 
    lequel cliquer.
    """

    # Prendre un screenshot de l'écran sur lequel on se trouve (la page PW)
    page.screenshot(
        path="scenarios_exadata/img/screenshot_ecran.png", full_page=True
    )

    # Trouver les coordonnées sur lesquelles on souhaite cliquer
    coords = trouver_coordonnees_image(image_a_verifier)

    # Compteur qui permets de savoir combien de temps on va boucler pour trouver l'image
    cpt = cpt_duree

    # Attendre de trouver les coordonnées
    while coords is None and cpt > 0:
        sleep(0.200)
        page.screenshot(
            path="scenarios_exadata/img/screenshot_ecran.png", full_page=True
        )
        coords = trouver_coordonnees_image(image_a_verifier)
        cpt = cpt - 1

    if obligatoire:
        if coords is None:
            raise Exception(f"Impossible de trouver l'image sur l'écran : {image_a_verifier}")
        else:
            return coords
    else:
        return coords