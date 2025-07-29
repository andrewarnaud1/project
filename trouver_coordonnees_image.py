“””
Module de comparaison et localisation d’images pour l’automatisation Exadata.

Ce module utilise OpenCV pour localiser des éléments d’interface en comparant
des images de référence avec des captures d’écran de l’interface Guacamole.
“””

import cv2
import numpy as np
import os
from typing import Optional, Tuple, List
import logging

# Configuration du logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

def trouver_coordonnees_image(
template_path: str,
screenshot_path: str = “scenarios_exadata/img/screenshot_ecran.png”,
confiance: float = 0.8,
debug: bool = False
) -> Optional[Tuple[float, float]]:
“””
Compare deux images et retourne les coordonnées du centre de l’image trouvée.

```
Cette fonction utilise la corrélation croisée normalisée pour localiser
une image template dans un screenshot plus large.

Args:
    template_path (str): Chemin vers l'image à rechercher (template)
    screenshot_path (str): Chemin vers la capture d'écran où chercher
    confiance (float): Seuil de confiance minimum (0.0 à 1.0). 
                      Plus la valeur est élevée, plus la correspondance doit être précise.
                      Valeur recommandée: 0.8
    debug (bool): Active les logs de débogage détaillés

Returns:
    Optional[Tuple[float, float]]: Coordonnées (x, y) du centre de l'image trouvée,
                                  ou None si l'image n'est pas trouvée avec la confiance requise

Raises:
    FileNotFoundError: Si l'un des fichiers image n'existe pas
    cv2.error: Si les images ne peuvent pas être lues (format invalide)

Example:
    >>> coords = trouver_coordonnees_image("images/bouton_connexion.png")
    >>> if coords:
    ...     print(f"Bouton trouvé aux coordonnées: {coords}")
    ... else:
    ...     print("Bouton non trouvé")
"""

# Vérification de l'existence des fichiers
if not os.path.exists(template_path):
    raise FileNotFoundError(f"Le fichier template n'existe pas: {template_path}")

if not os.path.exists(screenshot_path):
    raise FileNotFoundError(f"Le fichier screenshot n'existe pas: {screenshot_path}")

try:
    # Lecture des images
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)
    
    if screenshot is None:
        raise cv2.error(f"Impossible de lire le screenshot: {screenshot_path}")
    
    if template is None:
        raise cv2.error(f"Impossible de lire le template: {template_path}")

    if debug:
        logger.info(f"Screenshot dimensions: {screenshot.shape}")
        logger.info(f"Template dimensions: {template.shape}")

    # Vérification que le template n'est pas plus grand que le screenshot
    if (template.shape[0] > screenshot.shape[0] or 
        template.shape[1] > screenshot.shape[1]):
        logger.warning("Le template est plus grand que le screenshot")
        return None

    # Recherche de correspondance avec corrélation croisée normalisée
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    
    # Localisation du meilleur match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if debug:
        logger.info(f"Confiance trouvée: {max_val:.3f} (seuil: {confiance})")
        logger.info(f"Position du match: {max_loc}")

    # Vérification du seuil de confiance
    if max_val >= confiance:
        # Récupération des dimensions du template
        height, width = template.shape[:2]
        
        # Calcul des coordonnées du centre
        center_x = max_loc[0] + (width / 2)
        center_y = max_loc[1] + (height / 2)
        
        logger.info(f"Image trouvée '{os.path.basename(template_path)}' "
                   f"avec confiance {max_val:.3f} aux coordonnées ({center_x:.1f}, {center_y:.1f})")
        
        return (center_x, center_y)
    else:
        logger.warning(f"Image '{os.path.basename(template_path)}' non trouvée "
                      f"(confiance {max_val:.3f} < {confiance})")
        return None
        
except cv2.error as e:
    logger.error(f"Erreur OpenCV: {e}")
    raise
except Exception as e:
    logger.error(f"Erreur inattendue lors de la recherche d'image: {e}")
    raise
```

def trouver_toutes_coordonnees_image(
template_path: str,
screenshot_path: str = “scenarios_exadata/img/screenshot_ecran.png”,
confiance: float = 0.8
) -> List[Tuple[float, float]]:
“””
Trouve toutes les occurrences d’une image dans un screenshot.

```
Utile pour localiser plusieurs éléments identiques (ex: plusieurs boutons similaires).

Args:
    template_path (str): Chemin vers l'image à rechercher
    screenshot_path (str): Chemin vers la capture d'écran
    confiance (float): Seuil de confiance minimum

Returns:
    List[Tuple[float, float]]: Liste des coordonnées de tous les matches trouvés
"""

if not os.path.exists(template_path) or not os.path.exists(screenshot_path):
    return []

try:
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)
    
    if screenshot is None or template is None:
        return []

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    height, width = template.shape[:2]
    
    # Trouver tous les points au-dessus du seuil
    locations = np.where(result >= confiance)
    coordinates = []
    
    for pt in zip(*locations[::-1]):  # Switch x and y
        center_x = pt[0] + (width / 2)
        center_y = pt[1] + (height / 2)
        coordinates.append((center_x, center_y))
    
    logger.info(f"Trouvé {len(coordinates)} occurrences de '{os.path.basename(template_path)}'")
    return coordinates
    
except Exception as e:
    logger.error(f"Erreur lors de la recherche multiple: {e}")
    return []
```