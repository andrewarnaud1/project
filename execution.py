“””
execution.py - Version Simplifiée avec Module d’Initialisation

Gestion d’une exécution de scénario.
L’initialisation est déléguée au module d’initialisation.
Cette classe se concentre sur l’exécution des tests et la finalisation.
“””

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pytest

from src.utils.utils import contexte_actuel
from src.utils.api import inscrire_resultats_api
from .initialisation import initialiser_scenario

LOGGER = logging.getLogger(**name**)

class Execution:
“””
Classe d’exécution des scénarios.

```
L'initialisation est déléguée au module d'initialisation.
Cette classe se concentre sur l'exécution des tests et la finalisation.
"""

def __init__(self) -> None:
    """
    Initialise l'execution en utilisant le module d'initialisation.
    """
    methode_name = contexte_actuel(self)
    LOGGER.debug("[%s] ---- DEBUT ----", methode_name)
    
    # Date de début
    self.date = datetime.now()
    
    # === INITIALISATION VIA MODULE DÉDIÉ ===
    # Le module d'initialisation gère toute la logique de démarrage
    # et les erreurs avec inscription API appropriée
    self.config, self.donnees_scenario_api = initialiser_scenario()
    
    # === ATTRIBUTS D'EXÉCUTION ===
    self.duree = 0
    self.status = 3  # UNKNOWN par défaut
    self.commentaire = ""
    self.commentaire_initial = ""
    
    # Informations système (depuis la config)
    self.injecteur = os.getenv("HOSTNAME", "unknown")
    self.navigateur = self.config.get("navigateur", "unknown")
    self.interface_ip = "127.0.0.1"
    
    # Statuts initiaux
    self.status_initial = 3
    
    # Liste des étapes d'exécution
    self.etapes: List[Dict] = []
    self.compteur_etape = 0
    
    # URL initiale pour les rapports
    self.url_initiale_header = ""
    
    # Liste des éléments à flouter (pour screenshots)
    self.elts_flous = []
    
    LOGGER.info("[%s] ✅ Execution initialisée et prête pour les tests", methode_name)
    LOGGER.debug("[%s] ----  FIN  ----", methode_name)

def __str__(self) -> str:
    """Représentation textuelle de l'exécution"""
    return f"""
```

Execution:
date: {self.date}
duree: {self.duree}
status: {self.status}
commentaire: {self.commentaire}
injecteur: {self.injecteur}
navigateur: {self.navigateur}
etapes: {len(self.etapes)} étape(s)
scenario: {self.config.get(‘nom_scenario’, ‘N/A’)}
“””

```
def ajoute_etape(self, etape: Dict) -> None:
    """Ajoute une étape à la liste des étapes."""
    methode_name = contexte_actuel(self)
    LOGGER.debug("[%s] ---- DEBUT ----", methode_name)
    
    self.etapes.append(etape)
    
    LOGGER.debug("[%s] Étape ajoutée: %s", methode_name, etape.get("nom", "N/A"))
    LOGGER.debug("[%s] Total étapes: %d", methode_name, len(self.etapes))
    LOGGER.debug("[%s] ----  FIN  ----", methode_name)

def finalise(self):
    """Finalise le scénario, calcule la durée totale et agrège les statuts."""
    methode_name = contexte_actuel(self)
    LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

    # Calcul de la durée totale
    if self.etapes:
        self.duree = sum([float(etape["duree"]) for etape in self.etapes])
        
        # Le statut final est celui de la dernière étape
        derniere_etape = self.etapes[-1]
        self.status = derniere_etape["status"]
        self.commentaire = derniere_etape["commentaire"]
        
        # Statuts initiaux = finaux (pour compatibilité)
        self.status_initial = self.status
        self.commentaire_initial = self.commentaire
        
        LOGGER.info("[%s] Finalisation: %d étapes, statut=%s, durée=%.3fs", 
                   methode_name, len(self.etapes), self.status, self.duree)
    else:
        LOGGER.warning("[%s] Aucune étape exécutée", methode_name)
        
    LOGGER.debug("[%s] ----  FIN  ----", methode_name)

def save_to_json(self, filepath: str) -> dict:
    """Enregistre le scénario sous forme de fichier JSON."""
    methode_name = contexte_actuel(self)
    LOGGER.debug("[%s] ---- DEBUT ----", methode_name)
    
    data = {
        "identifiant": self.config.get("identifiant", ""),
        "scenario": self.config.get("nom_scenario", ""),
        "date": self.date.isoformat(),
        "duree": self.duree,
        "status": self.status,
        "nb_scene": len(self.etapes),
        "commentaire": self.commentaire,
        "injecteur": self.injecteur,
        "navigateur": self.navigateur,
        "interface_ip": self.interface_ip,
        "status_initial": self.status_initial,
        "commentaire_initial": self.commentaire_initial,
        "briques": self.etapes,
    }
    
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        LOGGER.info("[%s] Rapport JSON sauvegardé: %s", methode_name, filepath)
    except Exception as e:
        LOGGER.error("[%s] Erreur sauvegarde JSON: %s", methode_name, e)

    LOGGER.debug("[%s] ----  FIN  ----", methode_name)
    return data
```

# === FIXTURE PYTEST ===

@pytest.fixture(scope=“session”)
def execution():
“””
Crée un scénario unique pour tous les tests et le finalise à la fin.

```
L'initialisation est gérée automatiquement par le module d'initialisation
avec gestion des erreurs et inscription API appropriée.
"""
fixture_name = contexte_actuel()
LOGGER.debug("[Fixture SETUP %s] ----  DEBUT  ----", fixture_name)

# Création de l'exécution (initialisation automatique via le module)
execution_scenario = Execution()

LOGGER.debug("[Fixture SETUP %s] ----   FIN   ----", fixture_name)

# Retourne l'instance d'exécution pour tous les tests
yield execution_scenario

# === FINALISATION AUTOMATIQUE ===
LOGGER.debug("[Fixture FINAL %s] ----  DEBUT  ----", fixture_name)

try:
    # Finalise le scénario après tous les tests
    execution_scenario.finalise()

    # Génération du rapport JSON
    if execution_scenario.config.get("report_dir"):
        nom_rapport_json = f"{execution_scenario.config.get('report_dir')}/scenario.json"
        json_execution = execution_scenario.save_to_json(nom_rapport_json)
    else:
        # Pas de répertoire de rapport - créer quand même les données
        json_execution = {
            "identifiant": execution_scenario.config.get("identifiant", ""),
            "scenario": execution_scenario.config.get("nom_scenario", ""),
            "date": execution_scenario.date.isoformat(),
            "duree": execution_scenario.duree,
            "status": execution_scenario.status,
            "nb_scene": len(execution_scenario.etapes),
            "commentaire": execution_scenario.commentaire,
            "injecteur": execution_scenario.injecteur,
            "navigateur": execution_scenario.navigateur,
            "interface_ip": execution_scenario.interface_ip,
            "status_initial": execution_scenario.status_initial,
            "commentaire_initial": execution_scenario.commentaire_initial,
            "briques": execution_scenario.etapes,
        }

    # Inscription des résultats
    if execution_scenario.config.get("inscription"):
        inscrire_resultats_api(
            execution_scenario.config.get("url_base_api_injecteur"),
            json_execution,
        )
        LOGGER.info("[Fixture FINAL %s] ✅ Résultats inscrits en API", fixture_name)
    else:
        # Dump du JSON si inscription désactivée
        LOGGER.warning(
            "[Fixture FINAL %s] ⚠️ Scénario non inscrit (inscription = %s)",
            fixture_name,
            execution_scenario.config.get("inscription"),
        )
        LOGGER.info(
            "[Fixture FINAL %s] json scénario => \n%s",
            fixture_name,
            json.dumps(json_execution, ensure_ascii=False, indent=4),
        )

except Exception as e:
    LOGGER.error("[Fixture FINAL %s] Erreur lors de la finalisation: %s", fixture_name, e)
    
    # Même en cas d'erreur de finalisation, essayer d'inscrire un résultat d'erreur
    try:
        if execution_scenario.config.get("inscription"):
            json_erreur = {
                "identifiant": execution_scenario.config.get("identifiant", ""),
                "scenario": execution_scenario.config.get("nom_scenario", ""),
                "date": execution_scenario.date.isoformat(),
                "duree": execution_scenario.duree,
                "status": 2,  # Erreur
                "nb_scene": len(execution_scenario.etapes),
                "commentaire": f"Erreur lors de la finalisation: {e}",
                "injecteur": execution_scenario.injecteur,
                "navigateur": execution_scenario.navigateur,
                "interface_ip": execution_scenario.interface_ip,
                "status_initial": 2,
                "commentaire_initial": f"Erreur lors de la finalisation: {e}",
                "briques": execution_scenario.etapes,
            }
            
            inscrire_resultats_api(
                execution_scenario.config.get("url_base_api_injecteur"),
                json_erreur,
            )
            LOGGER.info("[Fixture FINAL %s] ✅ Erreur de finalisation inscrite", fixture_name)
    except:
        LOGGER.error("[Fixture FINAL %s] Échec inscription erreur de finalisation", fixture_name)

LOGGER.debug("[Fixture FINAL %s] ----   FIN   ----", fixture_name)
```