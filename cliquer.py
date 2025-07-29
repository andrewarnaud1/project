"""
Module d'action de click
"""

from playwright.sync_api import Page
from .verifier import verifier

def cliquer(
    image_click,
    page: Page,
    droit=False,
    obligatoire=True
):
    """
    Permets de cliquer sur un élément à partir d'une image.

    """

    coords = verifier(image_a_verifier=image_click, page=page, obligatoire=obligatoire)

    if obligatoire and coords or coords is not None:
        if droit:
            page.mouse.click(x=coords[0], y=coords[1], button="right")
        else:
            page.mouse.click(x=coords[0], y=coords[1])
    else:
        pass
