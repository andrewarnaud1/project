“””
initialisation.py

Module d’initialisation séquentiel pour le simulateur de tests automatisés.
Gère toutes les phases de démarrage et la logique d’inscription API.
“””

import os
import json
import logging
import pytest
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from src.utils.utils import contexte_actuel
from src.utils.api import lecture_api_scenario, inscrire_resultats_api
from src.utils.planning_execution import verifier_planning_execution
from .environnement import Environnement
from .configuration import Configuration
from src.utils.constantes import ConstantesSimulateur

LOGGER = logging.getLogger(**name**)

class ErreurInitialisation(Exception):
“”“Exception de base pour l’initialisation”””
pass

class ErreurPreAPI(ErreurInitialisation):
“”“Erreurs avant API - exit 1, pas d’inscription”””
pass

class ErreurPostAPI(ErreurInitialisation):
“”“Erreurs après API - exit 2, inscription obligatoire avec status=3”””
pass

class InitialisateurScenario:
“””
Gestionnaire d’initialisation séquentiel pour les scénarios.

```
Responsabilités :
- Chargement séquentiel des phases d'initialisation
- Gestion des erreurs avec inscription API appropriée
- Retour d'une configuration complète pour l'exécution
"""

def __init__(self):
    """Initialise l'initialisateur"""
    self.environnement: Optional[Dict] = None
    self.config: Optional[Dict] = None
    self.donnees_api: Optional[Dict] = None
    self.phase_courante = "INITIALISATION"
    self.api_chargee_avec_succes = False
    self.date_debut = datetime.now()
    
def initialiser(self) -> Tuple[Dict, Dict]:
    """
    Lance l'initialisation séquentielle complète.
    
    Returns:
        Tuple[Dict, Dict]: (configuration_complete, donnees_api)
        
    Raises:
        SystemExit: Avec code 1 (pré-API) ou 2 (post-API)
    """
    methode_name = contexte_actuel(self)
    LOGGER.info("[%s] ========== INITIALISATION SCÉNARIO ==========", methode_name)
    
    try:
        # === PHASES 1-4 : PRÉ-API (pas d'inscription en cas d'erreur) ===
        self._executer_phases_pre_api()
        
        # === PHASES 5-6 : POST-API (inscription obligatoire en cas d'erreur) ===
        self._executer_phases_post_api()
        
        LOGGER.info("[%s] ✅ Initialisation complète réussie", methode_name)
        return self.config, self.donnees_api
        
    except ErreurPreAPI as e:
        self._gerer_erreur_pre_api(e)
        pytest.exit(1)
        
    except ErreurPostAPI as e:
        self._gerer_erreur_post_api(e)
        pytest.exit(2)
        
    except Exception as e:
        # Erreur inattendue
        if self.api_chargee_avec_succes:
            self._gerer_erreur_post_api(ErreurPostAPI(f"Erreur inattendue: {e}"))
            pytest.exit(2)
        else:
            self._gerer_erreur_pre_api(ErreurPreAPI(f"Erreur inattendue: {e}"))
            pytest.exit(1)

def _executer_phases_pre_api(self):
    """Exécute les phases 1-4 sans inscription API possible"""
    self._phase_1_environnement()
    self._phase_2_configuration_base()
    self._phase_3_api_lecture()
    self._phase_4_verification_planning()
    
def _executer_phases_post_api(self):
    """Exécute les phases 5-6 avec inscription API obligatoire si erreur"""
    self._phase_5_configuration_finale()
    self._phase_6_repertoires()

# === PHASES PRÉ-API ===

def _phase_1_environnement(self):
    """Phase 1: Chargement et validation de l'environnement"""
    self.phase_courante = "CHARGEMENT_ENVIRONNEMENT"
    methode_name = contexte_actuel(self)
    LOGGER.info("[%s] === PHASE 1: ENVIRONNEMENT ===", methode_name)

    try:
        environnement_manager = Environnement()
        self.environnement = environnement_manager.charger_variables_environnement()
        LOGGER.info("[%s] ✅ Environnement chargé", methode_name)
        
    except Exception as e:
        raise ErreurPreAPI(f"Échec chargement environnement: {e}") from e

def _phase_2_configuration_base(self):
    """Phase 2: Chargement de la configuration de base (pour avoir l'identifiant)"""
    self.phase_courante = "CONFIGURATION_BASE"
    methode_name = contexte_actuel(self)
    LOGGER.info("[%s] === PHASE 2: CONFIGURATION BASE ===", methode_name)

    try:
        config_manager = Configuration(environnement=self.environnement)
        self.config = config_manager.creer_configuration()
        
        LOGGER.info("[%s] ✅ Configuration de base créée (identifiant disponible)", methode_name)
        
    except Exception as e:
        raise ErreurPreAPI(f"Échec création configuration de base: {e}") from e

def _phase_3_api_lecture(self):
    """Phase 3: Lecture des données API avec l'identifiant du scénario"""
    self.phase_courante = "LECTURE_API"
    methode_name = contexte_actuel(self)
    LOGGER.info("[%s] === PHASE 3: API LECTURE ===", methode_name)

    if not self.environnement.get("lecture", True):
        LOGGER.info("[%s] 📋 Lecture API désactivée", methode_name)
        self.donnees_api = {}
        return

    # Récupérer l'identifiant depuis la configuration
    identifiant = self.config.get("identifiant")
    if not identifiant:
        raise ErreurPreAPI("Identifiant scénario non trouvé dans la configuration")

    try:
        self.donnees_api = lecture_api_scenario(
            url_base_api_injecteur=self.environnement["url_base_api_injecteur"],
            identifiant_scenario=identifiant
        )
        self.api_chargee_avec_succes = True
        LOGGER.info("[%s] ✅ API chargée - Inscription possible désormais", methode_name)
        
    except Exception as e:
        raise ErreurPreAPI(f"Échec lecture API: {e}") from e

def _phase_4_verification_planning(self):
    """Phase 4: Vérification du planning d'exécution"""
    self.phase_courante = "VERIFICATION_PLANNING"
    methode_name = contexte_actuel(self)
    LOGGER.info("[%s] === PHASE 4: PLANNING ===", methode_name)

    if not self.donnees_api:
        LOGGER.info("[%s] 📋 Pas de données API - Planning ignoré", methode_name)
        return

    try:
        verifier_planning_execution(self.donnees_api)
        LOGGER.info("[%s] ✅ Planning respecté", methode_name)
        
    except SystemExit:
        # Planning non respecté - scénario ne devait pas tourner
        raise ErreurPreAPI("Planning d'exécution non respecté - Scénario arrêté normalement")
    except Exception as e:
        raise ErreurPreAPI(f"Erreur vérification planning: {e}") from e

# === PHASES POST-API ===

def _phase_5_configuration_finale(self):
    """Phase 5: Finalisation de la configuration avec les données API"""
    self.phase_courante = "CONFIGURATION_FINALE"
    methode_name = contexte_actuel(self)
    LOGGER.info("[%s] === PHASE 5: CONFIGURATION FINALE ===", methode_name)

    try:
        # Fusionner les données API dans la configuration si disponibles
        if self.donnees_api:
            # Ici tu peux ajouter la logique pour fusionner les données API
            # avec la configuration existante si nécessaire
            LOGGER.info("[%s] Fusion des données API avec la configuration", methode_name)
        
        LOGGER.info("[%s] ✅ Configuration finalisée", methode_name)
        
    except Exception as e:
        raise ErreurPostAPI(f"Échec finalisation configuration: {e}") from e

def _phase_6_repertoires(self):
    """Phase 6: Création des répertoires de sortie"""
    self.phase_courante = "CREATION_REPERTOIRES"
    methode_name = contexte_actuel(self)
    LOGGER.info("[%s] === PHASE 6: RÉPERTOIRES ===", methode_name)

    try:
        self._creer_repertoires_sortie()
        
        # Chemin spécial pour les scénarios exadata
        if self.config["type_scenario"] == ConstantesSimulateur.TYPE_SCENARIO_EXADATA:
            self._chemin_image_exadata()
            
        LOGGER.info("[%s] ✅ Répertoires créés", methode_name)
        
    except Exception as e:
        # Erreur non critique - continuer avec avertissement
        LOGGER.warning("[%s] ⚠️ Échec création répertoires: %s", methode_name, e)
        self.config["screenshot_dir"] = None
        self.config["report_dir"] = None

# === MÉTHODES UTILITAIRES ===

def _creer_repertoires_sortie(self):
    """Crée les répertoires de screenshots et rapports"""
    date_heure = self.date_debut
    date = date_heure.date()
    heure = date_heure.strftime("%H:%M:%S")

    if self.donnees_api:
        nom_app = self.donnees_api.get("application", {}).get("nom", "NO_API")
        nom_scenario = self.donnees_api.get("nom", self.config["nom_scenario"])
    else:
        nom_app = "NO_API"
        nom_scenario = self.config["nom_scenario"]

    self.config["screenshot_dir"] = (
        f"{self.config['output_path']}/screenshots/{nom_app}/{nom_scenario}/{date}/{heure}"
    )
    self.config["report_dir"] = (
        f"{self.config['output_path']}/rapports/{nom_app}/{nom_scenario}/{date}/{heure}"
    )

    Path(self.config["screenshot_dir"]).mkdir(parents=True, exist_ok=True)
    Path(self.config["report_dir"]).mkdir(parents=True, exist_ok=True)

def _chemin_image_exadata(self):
    """Ajout du chemin des images exadata si le scénario est un exadata"""
    self.config["chemin_images_exadata"] = (
        f"{self.environnement.get('scenarios_path')}/scenarios_exadata/images/{self.config['nom_scenario']}"
    )

# === GESTION D'ERREURS ===

def _gerer_erreur_pre_api(self, erreur: ErreurPreAPI):
    """Gère les erreurs de pré-API (pas d'inscription)"""
    methode_name = contexte_actuel(self)
    LOGGER.critical("[%s] ❌ ERREUR PRÉ-API: %s", methode_name, erreur)
    LOGGER.critical("[%s] Phase: %s", methode_name, self.phase_courante)
    print(f"❌ Erreur critique en phase {self.phase_courante}: {erreur}")
    print("ℹ️ Aucune inscription API (erreur avant chargement API ou planning non respecté)")

def _gerer_erreur_post_api(self, erreur: ErreurPostAPI):
    """Gère les erreurs post-API (inscription obligatoire avec status=3)"""
    methode_name = contexte_actuel(self)
    LOGGER.critical("[%s] ❌ ERREUR POST-API: %s", methode_name, erreur)
    LOGGER.critical("[%s] Phase: %s", methode_name, self.phase_courante)
    print(f"❌ Erreur critique en phase {self.phase_courante}: {erreur}")
    
    self._inscrire_erreur_initialisation(str(erreur))

def _inscrire_erreur_initialisation(self, message_erreur: str):
    """Inscrit une erreur d'initialisation (status=3) via l'API"""
    methode_name = contexte_actuel(self)
    
    # Vérifier si l'inscription est possible (API chargée + identifiant disponible)
    if not self.api_chargee_avec_succes:
        LOGGER.warning("[%s] ⚠️ API non chargée - Pas d'inscription", methode_name)
        return
        
    # Vérifier si l'identifiant est disponible
    identifiant = self.config.get("identifiant")
    if not identifiant:
        LOGGER.warning("[%s] ⚠️ Identifiant scénario non disponible - Pas d'inscription", methode_name)
        print("ℹ️ Pas d'inscription API (identifiant scénario manquant)")
        return
        
    if not self.config or not self.config.get("inscription"):
        LOGGER.warning("[%s] ⚠️ Inscription désactivée", methode_name)
        return

    try:
        duree_totale = (datetime.now() - self.date_debut).total_seconds()
        
        data_erreur = {
            "identifiant": identifiant,
            "scenario": self.config.get("nom_scenario", ""),
            "date": self.date_debut.isoformat(),
            "duree": duree_totale,
            "status": 3,  # Status UNKNOWN pour erreurs d'initialisation
            "nb_scene": 0,
            "commentaire": "Erreur lors de l'initialisation du scénario - Scénario non lancé",
            "injecteur": os.getenv("HOSTNAME", "unknown"),
            "navigateur": self.config.get("navigateur", "unknown"),
            "interface_ip": "127.0.0.1",
            "status_initial": 3,
            "commentaire_initial": "Erreur lors de l'initialisation du scénario - Scénario non lancé",
            "briques": []
        }
        
        inscrire_resultats_api(
            self.config["url_base_api_injecteur"],
            data_erreur
        )
        
        LOGGER.info("[%s] ✅ Erreur d'initialisation inscrite", methode_name)
        print("✅ Erreur d'initialisation inscrite en base")
        
    except Exception as e:
        LOGGER.error("[%s] ❌ Échec inscription: %s", methode_name, e)
        print(f"❌ Échec inscription: {e}")
        
        try:
            print("📄 Données d'erreur:")
            print(json.dumps(data_erreur, ensure_ascii=False, indent=2))
        except:
            pass
```

# === FONCTION UTILITAIRE ===

def initialiser_scenario() -> Tuple[Dict, Dict]:
“””
Fonction utilitaire pour initialiser un scénario.

```
Returns:
    Tuple[Dict, Dict]: (configuration_complete, donnees_api)
    
Raises:
    SystemExit: En cas d'erreur d'initialisation
"""
initialisateur = InitialisateurScenario()
return initialisateur.initialiser()
```