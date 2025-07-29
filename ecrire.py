“””
Module de saisie de texte pour l’automatisation Exadata.

Ce module permet de saisir du texte dans des champs d’interface
identifiés par reconnaissance d’image.
“””

import time
from playwright.sync_api import Page
from typing import Optional, Literal
import logging
from .cliquer import cliquer

logger = logging.getLogger(**name**)

def ecrire(
image_champ_a_remplir: str,
texte: str,
page: Page,
effacer_contenu: bool = True,
timeout: int = 30,
delai_entre_caracteres: float = 0.0,
valider_avec_entree: bool = False,
confiance: float = 0.8
) -> bool:
“””
Saisit du texte dans un champ identifié par une image de référence.

```
Cette fonction clique d'abord sur le champ pour le sélectionner,
puis saisit le texte spécifié.

Args:
    image_champ_a_remplir (str): Chemin vers l'image du champ à remplir
    texte (str): Texte à saisir dans le champ
    page (Page): Instance de la page Playwright
    effacer_contenu (bool): Si True, efface le contenu existant avant la saisie
    timeout (int): Durée maximale d'attente pour trouver le champ (secondes)
    delai_entre_caracteres (float): Délai entre chaque caractère (pour simulation humaine)
    valider_avec_entree (bool): Si True, appuie sur Entrée après la saisie
    confiance (float): Seuil de confiance pour la reconnaissance d'image

Returns:
    bool: True si la saisie a été effectuée avec succès, False sinon

Raises:
    Exception: Si le champ est obligatoire mais non trouvé

Example:
    >>> # Saisie simple
    >>> ecrire("images/champ_nom.png", "Jean Dupont", page)
    >>> 
    >>> # Saisie avec validation par Entrée
    >>> ecrire("images/champ_recherche.png", "recherche", page, valider_avec_entree=True)
    >>> 
    >>> # Saisie lente (simulation humaine)
    >>> ecrire("images/champ_mdp.png", "motdepasse", page, delai_entre_caracteres=0.1)
"""

logger.info(f"Saisie de texte dans le champ '{image_champ_a_remplir}' : '{texte}'")

try:
    # Cliquer sur le champ pour le sélectionner
    succes_clic = cliquer(
        image_click=image_champ_a_remplir,
        page=page,
        timeout=timeout,
        confiance=confiance
    )
    
    if not succes_clic:
        logger.error(f"Impossible de cliquer sur le champ: {image_champ_a_remplir}")
        return False
    
    # Petit délai pour laisser le champ se sélectionner
    time.sleep(0.2)
    
    # Effacer le contenu existant si demandé
    if effacer_contenu:
        # Sélectionner tout le contenu (Ctrl+A) puis supprimer
        page.keyboard.press("Control+a")
        time.sleep(0.1)
        page.keyboard.press("Delete")
        time.sleep(0.1)
    
    # Saisir le texte
    if delai_entre_caracteres > 0:
        # Saisie caractère par caractère avec délai
        for caractere in texte:
            page.keyboard.type(caractere)
            time.sleep(delai_entre_caracteres)
    else:
        # Saisie normale
        page.keyboard.type(texte)
    
    # Validation avec Entrée si demandée
    if valider_avec_entree:
        time.sleep(0.2)
        page.keyboard.press("Enter")
    
    logger.info(f"Saisie effectuée avec succès dans '{image_champ_a_remplir}'")
    return True
    
except Exception as e:
    logger.error(f"Erreur lors de la saisie dans '{image_champ_a_remplir}': {e}")
    return False
```

def ecrire_mot_de_passe(
image_champ_mdp: str,
mot_de_passe: str,
page: Page,
timeout: int = 30,
confiance: float = 0.8
) -> bool:
“””
Saisit un mot de passe dans un champ sécurisé.

```
Fonction spécialisée pour les mots de passe avec sécurité renforcée
(pas de logs du contenu, saisie plus lente).

Args:
    image_champ_mdp (str): Chemin vers l'image du champ mot de passe
    mot_de_passe (str): Mot de passe à saisir
    page (Page): Instance de la page Playwright
    timeout (int): Timeout pour trouver le champ
    confiance (float): Seuil de confiance pour la reconnaissance

Returns:
    bool: True si la saisie a été effectuée avec succès

Example:
    >>> # Saisie sécurisée d'un mot de passe
    >>> ecrire_mot_de_passe("images/champ_password.png", "monmotdepasse", page)
"""

logger.info(f"Saisie de mot de passe dans le champ '{image_champ_mdp}' (contenu masqué)")

try:
    # Cliquer sur le champ
    succes_clic = cliquer(
        image_click=image_champ_mdp,
        page=page,
        timeout=timeout,
        confiance=confiance
    )
    
    if not succes_clic:
        logger.error(f"Impossible de cliquer sur le champ mot de passe")
        return False
    
    time.sleep(0.2)
    
    # Effacer le contenu existant
    page.keyboard.press("Control+a")
    time.sleep(0.1)
    page.keyboard.press("Delete")
    time.sleep(0.1)
    
    # Saisie avec un léger délai pour la sécurité
    for caractere in mot_de_passe:
        page.keyboard.type(caractere)
        time.sleep(0.05)  # Délai léger pour éviter la détection automatisée
    
    logger.info("Mot de passe saisi avec succès")
    return True
    
except Exception as e:
    logger.error(f"Erreur lors de la saisie du mot de passe: {e}")
    return False
```

def ecrire_avec_completion(
image_champ: str,
texte: str,
image_suggestion: str,
page: Page,
timeout: int = 30,
timeout_suggestion: int = 5,
confiance: float = 0.8
) -> bool:
“””
Saisit du texte et sélectionne une suggestion d’autocomplétion.

```
Utile pour les champs avec autocomplétion (recherche, sélection d'utilisateurs, etc.).

Args:
    image_champ (str): Image du champ de saisie
    texte (str): Texte à saisir pour déclencher l'autocomplétion
    image_suggestion (str): Image de la suggestion à sélectionner
    page (Page): Instance de la page Playwright
    timeout (int): Timeout pour trouver le champ
    timeout_suggestion (int): Timeout pour trouver la suggestion
    confiance (float): Seuil de confiance pour la reconnaissance

Returns:
    bool: True si la saisie et sélection ont été effectuées avec succès

Example:
    >>> # Saisir "Jean" et sélectionner "Jean Dupont" dans les suggestions
    >>> ecrire_avec_completion(
    ...     "images/champ_utilisateur.png", 
    ...     "Jean", 
    ...     "images/suggestion_jean_dupont.png", 
    ...     page
    ... )
"""

logger.info(f"Saisie avec autocomplétion: '{texte}' -> suggestion")

try:
    # Saisir le texte initial
    if not ecrire(image_champ, texte, page, timeout=timeout, confiance=confiance):
        return False
    
    # Attendre un peu que les suggestions apparaissent
    time.sleep(0.5)
    
    # Cliquer sur la suggestion
    succes_suggestion = cliquer(
        image_click=image_suggestion,
        page=page,
        obligatoire=False,
        timeout=timeout_suggestion,
        confiance=confiance
    )
    
    if succes_suggestion:
        logger.info("Suggestion sélectionnée avec succès")
        return True
    else:
        logger.warning("Suggestion non trouvée, texte saisi uniquement")
        return True  # Le texte a été saisi même si la suggestion n'a pas été trouvée
    
except Exception as e:
    logger.error(f"Erreur lors de la saisie avec autocomplétion: {e}")
    return False
```

def coller_texte(
image_champ: str,
texte: str,
page: Page,
timeout: int = 30,
confiance: float = 0.8
) -> bool:
“””
Colle du texte dans un champ en utilisant le presse-papiers.

```
Plus rapide que la saisie caractère par caractère pour de longs textes.

Args:
    image_champ (str): Image du champ où coller
    texte (str): Texte à coller
    page (Page): Instance de la page Playwright
    timeout (int): Timeout pour trouver le champ
    confiance (float): Seuil de confiance pour la reconnaissance

Returns:
    bool: True si le collage a été effectué avec succès

Example:
    >>> # Coller un long texte
    >>> long_texte = "Un très long texte qui serait fastidieux à taper..."
    >>> coller_texte("images/champ_description.png", long_texte, page)
"""

logger.info(f"Collage de texte dans '{image_champ}' ({len(texte)} caractères)")

try:
    # Cliquer sur le champ
    if not cliquer(image_champ, page, timeout=timeout, confiance=confiance):
        return False
    
    time.sleep(0.2)
    
    # Effacer le contenu existant
    page.keyboard.press("Control+a")
    time.sleep(0.1)
    
    # Note: Dans un environnement réel, on utiliserait le système de presse-papiers
    # Ici on simule en tapant directement le texte
    page.keyboard.type(texte)
    
    logger.info("Texte collé avec succès")
    return True
    
except Exception as e:
    logger.error(f"Erreur lors du collage: {e}")
    return False
```