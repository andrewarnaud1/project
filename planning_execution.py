"""
Module de vérification du planning d'exécution des scénarios.

Ce module détermine si un scénario de test automatisé est autorisé à s'exécuter
à un moment donné en fonction des critères suivants :
- Gestion des jours fériés (flag_ferie)
- Respect des plages horaires définies dans le planning
"""

import logging
from datetime import datetime
from typing import Dict
import pytest

from src.utils.utils import contexte_actuel

from .plages_horaires import (
    extraire_plages_horaires_jour,
    verifier_plages_horaires
)

from .jours_feries import est_jour_ferie, verifier_flag_ferie


LOGGER = logging.getLogger(__name__)


def verifier_planning_execution(donnees_scenario_api: Dict) -> None:
    """
    Fonction principale de vérification du planning d'exécution.
    
    Cette fonction effectue toutes les vérifications nécessaires pour déterminer
    si un scénario peut s'exécuter maintenant :
    1. Vérification des jours fériés
    2. Vérification des plages horaires
    
    Args:
        donnees_scenario_api (Dict): Données du scénario récupérées via l'API
            Doit contenir : flag_ferie, planning
            
    Raises:
        pytest.exit(2): Si l'exécution n'est pas autorisée
        
    Example:
        donnees_api = {
            "flag_ferie": True,
            "planning": [
                {"jour": 1, "heure_debut": "07:00:00", "heure_fin": "12:00:00"},
                {"jour": 1, "heure_debut": "14:00:00", "heure_fin": "22:00:00"}
            ]
        }
        verifier_planning_execution(donnees_api)
    """
    methode_name = contexte_actuel()
    LOGGER.info("[%s] ======== VÉRIFICATION DU PLANNING D'EXÉCUTION ========", methode_name)
    LOGGER.debug("[%s] ---- DEBUT ----", methode_name)
    
    try:
        # === ÉTAPE 1: Récupération du contexte temporel ===
        maintenant = datetime.now()
        numero_jour_semaine = maintenant.isoweekday()  # 1=Lundi, 7=Dimanche
        heure_courante = maintenant.time()
        
        LOGGER.info("[%s] Contexte temporel:", methode_name)
        LOGGER.info("[%s]   - Date/heure: %s", methode_name, maintenant.strftime("%Y-%m-%d %H:%M:%S"))
        LOGGER.info("[%s]   - Jour semaine: %s", methode_name, numero_jour_semaine)
        
        # === ÉTAPE 2: Vérification des jours fériés ===
        LOGGER.info("[%s] --- Vérification jours fériés ---", methode_name)
        est_ferie = est_jour_ferie(maintenant)
        flag_ferie = donnees_scenario_api.get("flag_ferie")
        
        LOGGER.info("[%s]   - Est férié: %s", methode_name, est_ferie)
        LOGGER.info("[%s]   - Flag férié: %s", methode_name, flag_ferie)
        
        verifier_flag_ferie(flag_ferie, est_ferie)
        
        # === ÉTAPE 3: Extraction des plages horaires ===
        LOGGER.info("[%s] --- Vérification planning horaire ---", methode_name)
        planning = donnees_scenario_api.get("planning", [])

        LOGGER.info("[%s] Données API : %s", methode_name, donnees_scenario_api.get("planning", []))
        
        if not planning:
            message_erreur = "Aucun planning défini dans les données API"
            LOGGER.critical("[%s] %s", methode_name, message_erreur)
            print(message_erreur)
            pytest.exit(2)
        
        plages_jour = extraire_plages_horaires_jour(planning, numero_jour_semaine)
        
        # === ÉTAPE 4: Vérification des plages horaires ===
        verifier_plages_horaires(plages_jour, heure_courante)
        
        # === SUCCÈS ===
        message_succes = "Planning d'exécution respecté - Scénario autorisé à s'exécuter"
        LOGGER.info("[%s] %s", methode_name, message_succes)
        print(message_succes)  # Affichage immédiat pour Jenkins
        
    except Exception as e:
        if "pytest" in str(type(e)):
            # Re-lever les exceptions pytest.exit
            raise
        else:
            # Erreur inattendue
            message_erreur = f"Erreur lors de la vérification du planning: {e}"
            LOGGER.critical("[%s] %s", methode_name, message_erreur)
            print(message_erreur)
            pytest.exit(2)
    
    finally:
        LOGGER.debug("[%s] ---- FIN ----", methode_name)
        LOGGER.info("[%s] ========================================================", methode_name)
