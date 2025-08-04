"""
TODO Andrew : Ajouter la docstring après validation
"""

import logging
from datetime import datetime, time
from typing import Dict, List
import pytest

from src.utils.utils import contexte_actuel


LOGGER = logging.getLogger(__name__)


def extraire_plages_horaires_jour(planning: List[Dict], numero_jour: int) -> List[Dict]:
    """
    Extrait toutes les plages horaires définies pour un jour donné.
    
    Args:
        planning (List[Dict]): Liste des plages horaires du planning
        numero_jour (int): Numéro du jour de la semaine (1=Lundi, 7=Dimanche)
        
    Returns:
        List[Dict]: Liste des plages horaires pour le jour donné
        
    Example:
        planning = [
            {"jour": 1, "heure_debut": "07:00:00", "heure_fin": "12:00:00"},
            {"jour": 1, "heure_debut": "14:00:00", "heure_fin": "22:00:00"},
            {"jour": 2, "heure_debut": "08:00:00", "heure_fin": "18:00:00"}
        ]
        extraire_plages_horaires_jour(planning, 1) 
        # Retourne les 2 plages du lundi
    """
    methode_name = contexte_actuel()
    LOGGER.debug("[%s] ---- DEBUT ---- (jour=%s)", methode_name, numero_jour)
    
    plages_jour = []
    
    for plage in planning:
        if plage.get("jour") == numero_jour:
            plages_jour.append(plage)
            LOGGER.debug("[%s] Plage trouvée: %s-%s", 
                        methode_name, plage.get("heure_debut"), plage.get("heure_fin"))
    
    LOGGER.info("[%s] %d plage(s) horaire(s) trouvée(s) pour le jour %s", 
               methode_name, len(plages_jour), numero_jour)
    
    LOGGER.debug("[%s] ---- FIN ----", methode_name)
    return plages_jour


def valider_format_plage(plage: Dict) -> None:
    """
    Valide le format et la cohérence d'une plage horaire.
    
    Args:
        plage (Dict): Plage horaire à valider
            
    Raises:
        ValueError: Si la plage est invalide
    """
    methode_name = contexte_actuel()
    
    # Vérifier les  champs obligatoires
    if "heure_debut" not in plage or "heure_fin" not in plage:
        raise ValueError(f"Plage horaire incomplète: {plage}")
    
    try:
        # Valider et convertir les heures
        heure_debut = datetime.strptime(plage["heure_debut"], "%H:%M:%S").time()
        heure_fin = datetime.strptime(plage["heure_fin"], "%H:%M:%S").time()
        
        # Vérifier la cohérence temporelle
        if heure_debut >= heure_fin:
            raise ValueError(
                f"Plage horaire incohérente: début ({plage['heure_debut']}) >= "
                f"fin ({plage['heure_fin']})"
            )
            
        LOGGER.debug("[%s] Plage horaire valide: %s-%s", 
                    methode_name, plage["heure_debut"], plage["heure_fin"])
        
    except ValueError as e:
        if "time data" in str(e):
            raise ValueError(f"Format d'heure invalide dans la plage: {plage}") from e
        raise


def est_dans_plage_horaire(heure_courante: time, plage: Dict) -> bool:
    """
    Vérifie si une heure est comprise dans une plage horaire donnée.
    
    Args:
        heure_courante (time): Heure à vérifier
        plage (Dict): Plage horaire avec heure_debut et heure_fin
        
    Returns:
        bool: True si l'heure est dans la plage, False sinon
    """
    methode_name = contexte_actuel()
    
    try:
        # Valider la plage avant utilisation
        valider_format_plage(plage)
        
        heure_debut = datetime.strptime(plage["heure_debut"], "%H:%M:%S").time()
        heure_fin = datetime.strptime(plage["heure_fin"], "%H:%M:%S").time()
        
        # Vérifier si l'heure courante est dans la plage (bornes incluses)
        dans_plage = heure_debut <= heure_courante <= heure_fin
        
        LOGGER.debug("[%s] Heure %s %s dans la plage %s-%s", 
                    methode_name, heure_courante, 
                    "EST" if dans_plage else "N'EST PAS",
                    heure_debut, heure_fin)
        
        return dans_plage
        
    except ValueError as e:
        LOGGER.error("[%s] Erreur validation plage: %s", methode_name, e)
        return False


def verifier_plages_horaires(plages_jour: List[Dict], heure_courante: time) -> None:
    """
    Vérifie si l'heure courante est autorisée selon les plages horaires du jour.
    
    Args:
        plages_jour (List[Dict]): Liste des plages horaires du jour
        heure_courante (time): Heure courante à vérifier
        
    Raises:
        pytest.exit(2): Si l'heure courante n'est dans aucune plage autorisée
    """
    methode_name = contexte_actuel()
    LOGGER.debug("[%s] ---- DEBUT ---- (%d plages à vérifier)", 
                methode_name, len(plages_jour))
    
    if not plages_jour:
        message_erreur = "❌ Aucune plage horaire définie pour ce jour"
        LOGGER.critical("[%s] %s", methode_name, message_erreur)
        print(message_erreur)
        pytest.exit(2)
    
    # Vérifier chaque plage horaire du jour
    for i, plage in enumerate(plages_jour, 1):
        LOGGER.debug("[%s] Vérification plage %d/%d", methode_name, i, len(plages_jour))
        
        if est_dans_plage_horaire(heure_courante, plage):
            message_succes = (
                f"✅ Exécution autorisée dans la plage "
                f"{plage['heure_debut']}-{plage['heure_fin']}"
            )
            LOGGER.info("[%s] %s", methode_name, message_succes)
            LOGGER.debug("[%s] ---- FIN ---- (succès)", methode_name)
            return  # Sortie anticipée dès qu'une plage est valide
    
    # Aucune plage n'est valide - construire message d'erreur détaillé
    plages_str = " ".join([f"{p['heure_debut']}-{p['heure_fin']}" for p in plages_jour])
    message_erreur = (
        f"❌ Heure actuelle ({heure_courante.strftime('%H:%M:%S')}) "
        f"hors des plages autorisées: {plages_str}"
    )
    
    LOGGER.critical("[%s] %s", methode_name, message_erreur)
    print(message_erreur)
    pytest.exit(2)
