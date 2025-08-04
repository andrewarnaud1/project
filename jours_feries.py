"""
TODO Andrew : Ajouter la docstring après validation
"""

import logging
from datetime import datetime
from typing import Optional
import pytest

from src.utils.utils import contexte_actuel

try:
    from jours_feries_france import JoursFeries
    JOURS_FERIES_DISPONIBLE = True
except ImportError:
    JOURS_FERIES_DISPONIBLE = False
    logging.warning("Bibliothèque jours-feries-france non disponible. "
                   "Vérification des jours fériés désactivée.")

LOGGER = logging.getLogger(__name__)


def est_jour_ferie(date_verification: datetime) -> bool:
    """
    Vérifie si une date donnée est un jour férié en France.
    
    Args:
        date_verification (datetime): Date à vérifier
        
    Returns:
        bool: True si la date est un jour férié, False sinon
        
    Note:
        Si la bibliothèque jours-feries-france n'est pas disponible,
        retourne toujours False (pas de vérification des jours fériés).
    """
    methode_name = contexte_actuel()
    LOGGER.debug("[%s] ---- DEBUT ----", methode_name)
    
    if not JOURS_FERIES_DISPONIBLE:
        LOGGER.debug("[%s] Bibliothèque jours fériés non disponible", methode_name)
        return False
    
    try:
        # Récupérer tous les jours fériés de l'année
        jours_feries = JoursFeries.for_year(date_verification.year)
        
        # Vérifier si la date est dans la liste des jours fériés
        date_seule = date_verification.date()
        for nom_ferie, date_ferie in jours_feries.items():
            if date_ferie == date_seule:
                LOGGER.info("[%s] Jour férié détecté: %s (%s)", 
                          methode_name, nom_ferie, date_ferie)
                return True
                
        LOGGER.debug("[%s] Pas un jour férié: %s", methode_name, date_seule)
        return False
        
    except Exception as e:
        LOGGER.warning("[%s] Erreur lors de la vérification des jours fériés: %s", 
                      methode_name, e)
        return False
    finally:
        LOGGER.debug("[%s] ---- FIN ----", methode_name)


def verifier_flag_ferie(flag_ferie: Optional[bool], est_ferie: bool) -> None:
    """
    Vérifie si l'exécution est autorisée un jour férié.
    
    Args:
        flag_ferie (Optional[bool]): Flag d'autorisation des jours fériés
            - True: autorisé les jours fériés
            - False/None: interdit les jours fériés
        est_ferie (bool): True si nous sommes un jour férié
        
    Raises:
        pytest.exit(2): Si l'exécution est interdite un jour férié
    """
    methode_name = contexte_actuel()
    LOGGER.debug("[%s] ---- DEBUT ---- (flag_ferie=%s, est_ferie=%s)", 
                methode_name, flag_ferie, est_ferie)
    
    if est_ferie and flag_ferie is not True:
        message_erreur = (
            "❌ Exécution interdite : scénario non autorisé les jours fériés "
            f"(flag_ferie={flag_ferie})"
        )
        LOGGER.critical("[%s] %s", methode_name, message_erreur)
        print(message_erreur)  # Affichage immédiat pour Jenkins
        pytest.exit(2)
    
    if est_ferie and flag_ferie is True:
        LOGGER.info("[%s] ✅ Exécution autorisée un jour férié (flag_ferie=True)", 
                   methode_name)
    
    LOGGER.debug("[%s] ---- FIN ----", methode_name)

