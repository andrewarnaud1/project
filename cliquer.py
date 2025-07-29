“””
Module d’actions de clic pour l’automatisation Exadata.

Ce module permet d’effectuer des clics sur des éléments d’interface
identifiés par reconnaissance d’image.
“””

import time
from playwright.sync_api import Page
from typing import Optional, Literal
import logging
from .verifier import verifier

logger = logging.getLogger(**name**)

def cliquer(
image_click: str,
page: Page,
bouton: Literal[“left”, “right”, “middle”] = “left”,
obligatoire: bool = True,
timeout: int = 30,
double_clic: bool = False,
delai_apres_clic: float = 0.5,
confiance: float = 0.8
) -> bool:
“””
Clique sur un élément identifié par une image de référence.

```
Cette fonction localise d'abord l'élément sur l'écran, puis effectue
le clic aux coordonnées trouvées.

Args:
    image_click (str): Chemin vers l'image de l'élément sur lequel cliquer
    page (Page): Instance de la page Playwright
    bouton (str): Bouton de souris à utiliser ("left", "right", "middle")
    obligatoire (bool): Si True, lève une exception si l'élément n'est pas trouvé
    timeout (int): Durée maximale d'attente pour trouver l'élément (secondes)
    double_clic (bool): Si True, effectue un double-clic
    delai_apres_clic (float): Délai d'attente après le clic (secondes)
    confiance (float): Seuil de confiance pour la reconnaissance d'image

Returns:
    bool: True si le clic a été effectué, False sinon

Raises:
    Exception: Si l'élément est obligatoire mais non trouvé

Example:
    >>> # Clic gauche simple
    >>> cliquer("images/bouton_valider.png", page)
    >>> 
    >>> # Clic droit avec timeout personnalisé
    >>> cliquer("images/fichier.png", page, bouton="right", timeout=10)
    >>> 
    >>> # Double-clic optionnel
    >>> success = cliquer("images/icone.png", page, double_clic=True, obligatoire=False)
"""

logger.info(f"Tentative de clic sur '{image_click}' "
           f"(bouton: {bouton}, double: {double_clic}, timeout: {timeout}s)")

try:
    # Recherche de l'élément
    coords = verifier(
        image_a_verifier=image_click,
        page=page,
        obligatoire=obligatoire,
        timeout=timeout,
        confiance=confiance
    )
    
    # Vérification si l'élément a été trouvé
    if coords is None:
        if obligatoire:
            # Cette exception ne devrait jamais être atteinte car verifier() lève déjà une exception
            raise Exception(f"Impossible de localiser l'élément pour cliquer: {image_click}")
        else:
            logger.warning(f"Élément non trouvé, clic ignoré: {image_click}")
            return False
    
    # Effectuer le clic
    x, y = coords
    
    if double_clic:
        logger.info(f"Double-clic {bouton} aux coordonnées ({x:.1f}, {y:.1f})")
        page.mouse.dblclick(x=x, y=y, button=bouton)
    else:
        logger.info(f"Clic {bouton} aux coordonnées ({x:.1f}, {y:.1f})")
        page.mouse.click(x=x, y=y, button=bouton)
    
    # Délai après clic pour laisser le temps à l'interface de réagir
    if delai_apres_clic > 0:
        time.sleep(delai_apres_clic)
    
    logger.info(f"Clic effectué avec succès sur '{image_click}'")
    return True
    
except Exception as e:
    logger.error(f"Erreur lors du clic sur '{image_click}': {e}")
    if obligatoire:
        raise
    return False
```

def cliquer_et_maintenir(
image_click: str,
page: Page,
duree: float = 1.0,
timeout: int = 30,
confiance: float = 0.8
) -> bool:
“””
Clique et maintient le bouton enfoncé sur un élément.

```
Utile pour les actions de drag & drop ou les menus contextuels
qui nécessitent un clic maintenu.

Args:
    image_click (str): Chemin vers l'image de l'élément
    page (Page): Instance de la page Playwright
    duree (float): Durée de maintien du clic en secondes
    timeout (int): Timeout pour trouver l'élément
    confiance (float): Seuil de confiance pour la reconnaissance

Returns:
    bool: True si l'action a été effectuée avec succès

Example:
    >>> # Maintenir un clic pendant 2 secondes
    >>> cliquer_et_maintenir("images/slider.png", page, duree=2.0)
"""

logger.info(f"Clic maintenu sur '{image_click}' pendant {duree}s")

try:
    coords = verifier(
        image_a_verifier=image_click,
        page=page,
        timeout=timeout,
        confiance=confiance
    )
    
    if coords is None:
        return False
    
    x, y = coords
    
    # Commencer le clic (bouton enfoncé)
    page.mouse.move(x, y)
    page.mouse.down()
    
    # Maintenir pendant la durée spécifiée
    time.sleep(duree)
    
    # Relâcher le bouton
    page.mouse.up()
    
    logger.info(f"Clic maintenu effectué avec succès")
    return True
    
except Exception as e:
    logger.error(f"Erreur lors du clic maintenu: {e}")
    return False
```

def glisser_deposer(
image_source: str,
image_destination: str,
page: Page,
timeout: int = 30,
confiance: float = 0.8
) -> bool:
“””
Effectue un glisser-déposer entre deux éléments.

```
Args:
    image_source (str): Image de l'élément à faire glisser
    image_destination (str): Image de la zone de destination
    page (Page): Instance de la page Playwright
    timeout (int): Timeout pour trouver les éléments
    confiance (float): Seuil de confiance pour la reconnaissance

Returns:
    bool: True si l'action a été effectuée avec succès

Example:
    >>> # Glisser un fichier vers une zone de téléchargement
    >>> glisser_deposer("images/fichier.png", "images/zone_depot.png", page)
"""

logger.info(f"Glisser-déposer de '{image_source}' vers '{image_destination}'")

try:
    # Trouver l'élément source
    coords_source = verifier(
        image_a_verifier=image_source,
        page=page,
        timeout=timeout,
        confiance=confiance
    )
    
    if coords_source is None:
        logger.error("Élément source non trouvé")
        return False
    
    # Trouver l'élément destination
    coords_dest = verifier(
        image_a_verifier=image_destination,
        page=page,
        timeout=timeout,
        confiance=confiance
    )
    
    if coords_dest is None:
        logger.error("Élément destination non trouvé")
        return False
    
    # Effectuer le glisser-déposer
    x_src, y_src = coords_source
    x_dest, y_dest = coords_dest
    
    page.mouse.move(x_src, y_src)
    page.mouse.down()
    page.mouse.move(x_dest, y_dest)
    page.mouse.up()
    
    logger.info(f"Glisser-déposer effectué: ({x_src:.1f},{y_src:.1f}) -> ({x_dest:.1f},{y_dest:.1f})")
    return True
    
except Exception as e:
    logger.error(f"Erreur lors du glisser-déposer: {e}")
    return False
```