“””
Module de vérification d’éléments d’interface pour l’automatisation Exadata.

Ce module permet de vérifier la présence d’éléments sur l’interface Guacamole
en prenant des captures d’écran et en recherchant des images de référence.
“””

import time
import os
from playwright.sync_api import Page
from typing import Optional, Tuple
import logging
from .trouver_coordonnees_image import trouver_coordonnees_image

logger = logging.getLogger(**name**)

def verifier(
image_a_verifier: str,
page: Page,
obligatoire: bool = True,
timeout: int = 30,
intervalle_verification: float = 0.2,
confiance: float = 0.8,
screenshot_dir: str = “scenarios_exadata/img”
) -> Optional[Tuple[float, float]]:
“””
Vérifie qu’un élément existe sur la page en recherchant une image de référence.

```
Cette fonction prend des captures d'écran répétées jusqu'à trouver l'élément
recherché ou jusqu'à expiration du timeout.

Args:
    image_a_verifier (str): Chemin vers l'image de référence à rechercher
    page (Page): Instance de la page Playwright pour les captures d'écran
    obligatoire (bool): Si True, lève une exception si l'élément n'est pas trouvé.
                       Si False, retourne None silencieusement.
    timeout (int): Durée maximale d'attente en secondes (défaut: 30s)
    intervalle_verification (float): Intervalle entre les vérifications en secondes (défaut: 0.2s)
    confiance (float): Seuil de confiance pour la reconnaissance d'image (défaut: 0.8)
    screenshot_dir (str): Répertoire pour sauvegarder les captures d'écran

Returns:
    Optional[Tuple[float, float]]: Coordonnées (x, y) du centre de l'élément trouvé,
                                  ou None si non trouvé et non obligatoire

Raises:
    Exception: Si l'élément est obligatoire mais non trouvé dans le délai imparti
    FileNotFoundError: Si l'image de référence n'existe pas

Example:
    >>> # Vérification obligatoire avec timeout de 10 secondes
    >>> coords = verifier("images/bouton_valider.png", page, timeout=10)
    >>> 
    >>> # Vérification optionnelle
    >>> coords = verifier("images/popup_erreur.png", page, obligatoire=False)
    >>> if coords:
    ...     print("Popup d'erreur détectée")
"""

# Vérification de l'existence de l'image de référence
if not os.path.exists(image_a_verifier):
    raise FileNotFoundError(f"L'image de référence n'existe pas: {image_a_verifier}")

# Création du répertoire de screenshots si nécessaire
os.makedirs(screenshot_dir, exist_ok=True)
screenshot_path = os.path.join(screenshot_dir, "screenshot_ecran.png")

# Conversion du timeout en nombre d'itérations
nb_iterations = int(timeout / intervalle_verification)
iteration_actuelle = 0

logger.info(f"Recherche de l'élément '{os.path.basename(image_a_verifier)}' "
           f"(timeout: {timeout}s, intervalle: {intervalle_verification}s)")

# Première capture d'écran
try:
    page.screenshot(path=screenshot_path, full_page=True)
except Exception as e:
    logger.error(f"Erreur lors de la capture d'écran: {e}")
    if obligatoire:
        raise Exception(f"Impossible de prendre une capture d'écran: {e}")
    return None

# Première vérification
coords = trouver_coordonnees_image(
    template_path=image_a_verifier,
    screenshot_path=screenshot_path,
    confiance=confiance
)

# Boucle d'attente si l'élément n'est pas trouvé immédiatement
while coords is None and iteration_actuelle < nb_iterations:
    time.sleep(intervalle_verification)
    iteration_actuelle += 1
    
    # Log de progression tous les 25 essais (environ toutes les 5 secondes par défaut)
    if iteration_actuelle % 25 == 0:
        temps_ecoule = iteration_actuelle * intervalle_verification
        logger.info(f"Recherche en cours... ({temps_ecoule:.1f}s/{timeout}s)")
    
    try:
        # Nouvelle capture d'écran
        page.screenshot(path=screenshot_path, full_page=True)
        
        # Nouvelle vérification
        coords = trouver_coordonnees_image(
            template_path=image_a_verifier,
            screenshot_path=screenshot_path,
            confiance=confiance
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification (itération {iteration_actuelle}): {e}")
        if obligatoire:
            raise Exception(f"Erreur lors de la vérification: {e}")

# Gestion du résultat
temps_total = iteration_actuelle * intervalle_verification

if coords is not None:
    logger.info(f"Élément trouvé après {temps_total:.1f}s aux coordonnées {coords}")
    return coords
else:
    message = (f"Élément '{os.path.basename(image_a_verifier)}' non trouvé "
              f"après {temps_total:.1f}s ({iteration_actuelle} tentatives)")
    
    if obligatoire:
        logger.error(message)
        raise Exception(f"Impossible de trouver l'image sur l'écran : {image_a_verifier}")
    else:
        logger.warning(message)
        return None
```

def attendre_disparition(
image_a_verifier: str,
page: Page,
timeout: int = 30,
intervalle_verification: float = 0.2
) -> bool:
“””
Attend qu’un élément disparaisse de l’écran.

```
Utile pour attendre la fermeture de popups, la fin de chargements, etc.

Args:
    image_a_verifier (str): Chemin vers l'image qui doit disparaître
    page (Page): Instance de la page Playwright
    timeout (int): Durée maximale d'attente en secondes
    intervalle_verification (float): Intervalle entre les vérifications

Returns:
    bool: True si l'élément a disparu, False si encore présent après timeout

Example:
    >>> # Attendre que le spinner de chargement disparaisse
    >>> if attendre_disparition("images/spinner.png", page, timeout=60):
    ...     print("Chargement terminé")
    ... else:
    ...     print("Timeout: chargement trop long")
"""

logger.info(f"Attente de disparition de '{os.path.basename(image_a_verifier)}'")

nb_iterations = int(timeout / intervalle_verification)

for i in range(nb_iterations):
    coords = verifier(
        image_a_verifier=image_a_verifier,
        page=page,
        obligatoire=False,
        timeout=intervalle_verification
    )
    
    if coords is None:
        logger.info(f"Élément disparu après {i * intervalle_verification:.1f}s")
        return True
    
    time.sleep(intervalle_verification)

logger.warning(f"Élément encore présent après {timeout}s")
return False
```