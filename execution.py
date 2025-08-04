"""
execution.py - Version Refactorisée

Gestion séquentielle des phases d'initialisation et d'exécution d'un scénario.
Gère les erreurs avec les règles d'inscription API appropriées.
"""

import os
import re
from datetime import datetime
from pathlib import Path
import json
import logging
import pytest

from src.utils import load_yaml_file
from src.utils.utils import contexte_actuel
from src.utils.api import lecture_api_scenario, inscrire_resultats_api
from src.utils.planning_execution import verifier_planning_execution
from .environnement import Environnement
from .configuration import Configuration
from src.utils.constantes import ConstantesSimulateur

LOGGER = logging.getLogger(__name__)


class ErreurSimulateur(Exception):
    """Exception de base du simulateur"""
    pass


class ErreurPreExecution(ErreurSimulateur):
    """Erreurs avant API - exit 1, pas d'inscription"""
    pass


class ErreurPostAPI(ErreurSimulateur):
    """Erreurs après API - exit 2, inscription obligatoire avec status=3"""
    pass


class Execution:
    """Classe d'exécution des scénarios avec initialisation séquentielle"""

    def __init__(self) -> None:
        """
        Initialise l'execution avec un processus séquentiel :
        1. Environnement
        2. API (si activée)
        3. Planning (si API active)
        4. Configuration
        5. Répertoires
        """
        self.date = datetime.now()
        self.duree = 0
        self.status = 3  # UNKNOWN par défaut
        self.commentaire = ""
        self.injecteur = os.getenv("HOSTNAME", "unknown")
        self.navigateur = ""
        self.interface_ip = "127.0.0.1"
        self.status_initial = 3
        self.commentaire_initial = ""
        self.etapes = []
        self.compteur_etape = 0
        self.url_initiale_header = ""
        self.elts_flous = []

        # Variables d'état pour gérer les erreurs
        self.environnement = {}
        self.donnees_scenario_api = {}
        self.config = {}
        self.api_chargee_avec_succes = False
        self.phase_courante = "INITIALISATION"

        try:
            # === PHASE 1-3 : PRÉ-EXÉCUTION (pas d'inscription en cas d'erreur) ===
            self._phase_1_environnement()
            self._phase_2_api_lecture()
            self._phase_3_verification_planning()
            
            # === PHASE 4-5 : POST-API (inscription obligatoire en cas d'erreur) ===
            self._phase_4_configuration()
            self._phase_5_repertoires()
            
            LOGGER.info("[Execution] ✅ Initialisation complète réussie")
            
        except ErreurPreExecution as e:
            self._gerer_erreur_pre_execution(e)
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
                self._gerer_erreur_pre_execution(ErreurPreExecution(f"Erreur inattendue: {e}"))
                pytest.exit(1)

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
            raise ErreurPreExecution(f"Échec chargement environnement: {e}") from e

    def _phase_2_api_lecture(self):
        """Phase 2: Lecture des données API (si activée)"""
        self.phase_courante = "LECTURE_API"
        methode_name = contexte_actuel(self)
        LOGGER.info("[%s] === PHASE 2: API LECTURE ===", methode_name)

        if not self.environnement.get("lecture", True):
            LOGGER.info("[%s] 📋 Lecture API désactivée", methode_name)
            self.donnees_scenario_api = {}
            return

        try:
            self.donnees_scenario_api = lecture_api_scenario(
                url_base_api_injecteur=self.environnement["url_base_api_injecteur"],
                identifiant_scenario=self.environnement["identifiant"]
            )
            self.api_chargee_avec_succes = True
            LOGGER.info("[%s] ✅ API chargée - Inscription possible désormais", methode_name)
            
        except Exception as e:
            raise ErreurPreExecution(f"Échec lecture API: {e}") from e

    def _phase_3_verification_planning(self):
        """Phase 3: Vérification du planning d'exécution"""
        self.phase_courante = "VERIFICATION_PLANNING"
        methode_name = contexte_actuel(self)
        LOGGER.info("[%s] === PHASE 3: PLANNING ===", methode_name)

        if not self.donnees_scenario_api:
            LOGGER.info("[%s] 📋 Pas de données API - Planning ignoré", methode_name)
            return

        try:
            verifier_planning_execution(self.donnees_scenario_api)
            LOGGER.info("[%s] ✅ Planning respecté", methode_name)
            
        except SystemExit:
            # Planning non respecté - scénario ne devait pas tourner
            raise ErreurPreExecution("Planning d'exécution non respecté - Scénario arrêté normalement")
        except Exception as e:
            raise ErreurPreExecution(f"Erreur vérification planning: {e}") from e

    def _phase_4_configuration(self):
        """Phase 4: Création de la configuration finale"""
        self.phase_courante = "CREATION_CONFIGURATION"
        methode_name = contexte_actuel(self)
        LOGGER.info("[%s] === PHASE 4: CONFIGURATION ===", methode_name)

        try:
            config_manager = Configuration(environnement=self.environnement)
            self.config = config_manager.creer_configuration()
            
            # Mise à jour des attributs de l'exécution
            self.navigateur = self.config.get("navigateur", "unknown")
            
            LOGGER.info("[%s] ✅ Configuration créée", methode_name)
            
        except Exception as e:
            raise ErreurPostAPI(f"Échec création configuration: {e}") from e

    def _phase_5_repertoires(self):
        """Phase 5: Création des répertoires de sortie"""
        self.phase_courante = "CREATION_REPERTOIRES"
        methode_name = contexte_actuel(self)
        LOGGER.info("[%s] === PHASE 5: RÉPERTOIRES ===", methode_name)

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

    def _creer_repertoires_sortie(self):
        """Crée les répertoires de screenshots et rapports"""
        date_heure = self.date
        date = date_heure.date()
        heure = date_heure.strftime("%H:%M:%S")

        if self.donnees_scenario_api:
            nom_app = self.donnees_scenario_api.get("application", {}).get("nom", "NO_API")
            nom_scenario = self.donnees_scenario_api.get("nom", self.config["nom_scenario"])
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

    def _gerer_erreur_pre_execution(self, erreur: ErreurPreExecution):
        """Gère les erreurs de pré-exécution (pas d'inscription API)"""
        methode_name = contexte_actuel(self)
        LOGGER.critical("[%s] ❌ ERREUR PRÉ-EXÉCUTION: %s", methode_name, erreur)
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
        identifiant = self.config.get("identifiant") or self.environnement.get("identifiant")
        if not identifiant:
            LOGGER.warning("[%s] ⚠️ Identifiant scénario non disponible - Pas d'inscription", methode_name)
            print("ℹ️ Pas d'inscription API (identifiant scénario manquant)")
            return
            
        if not self.config or not self.config.get("inscription"):
            LOGGER.warning("[%s] ⚠️ Inscription désactivée", methode_name)
            return

        try:
            duree_totale = (datetime.now() - self.date).total_seconds()
            
            data_erreur = {
                "identifiant": identifiant,  # Utilise l'identifiant vérifié
                "scenario": self.config.get("nom_scenario", ""),
                "date": self.date.isoformat(),
                "duree": duree_totale,
                "status": 3,  # Status UNKNOWN pour erreurs d'initialisation
                "nb_scene": 0,
                "commentaire": "Erreur lors de l'initialisation du scénario - Scénario non lancé",
                "injecteur": self.injecteur,
                "navigateur": self.navigateur,
                "interface_ip": self.interface_ip,
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

    # === MÉTHODES EXISTANTES INCHANGÉES ===
    
    def __str__(self) -> str:
        return f"""
execution 
    date : {self.date}
    duree : {self.duree}
    status : {self.status}
    commentaire : {self.commentaire}
    injecteur : {self.injecteur}
    navigateur : {self.navigateur}
    interface_ip : {self.interface_ip}
    status_initial : {self.status_initial}
    commentaire_initial : {self.commentaire_initial}
    etapes : {self.etapes}
    config : {self.config}
"""

    def ajoute_etape(self, etape: dict) -> None:
        """Ajout d'une étape self.etape (pour construire le rapport final)."""
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)
        self.etapes.append(etape)
        LOGGER.debug("[%s] ----  FIN  ----", methode_name)

    def finalise(self):
        """Finalise le scénario, calcule la durée totale et agrège les statuts."""
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        # Calcul de la durée totale
        self.duree = sum([float(etape["duree"]) for etape in self.etapes])

        # Cumul seulement si il y a des étapes
        if len(self.etapes) > 0:
            self.status = self.etapes[-1]["status"]
            LOGGER.debug("[%s] self.status => %s ", methode_name, self.etapes[-1]["status"])
            self.status_initial = self.etapes[-1]["status"]
            LOGGER.debug("[%s] self.status_initial => %s ", methode_name, self.etapes[-1]["status"])
            self.commentaire = self.etapes[-1]["commentaire"]
            self.commentaire_initial = self.etapes[-1]["commentaire"]
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
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        LOGGER.debug("[%s] ----  FIN  ----", methode_name)
        return data


# === FIXTURE PYTEST INCHANGÉE ===

@pytest.fixture(scope="session")
def execution():
    """Crée un scénario unique pour tous les tests et le finalise à la fin."""
    fixture_name = contexte_actuel()
    LOGGER.debug("[Fixture SETUP %s] ----  DEBUT  ----", fixture_name)

    execution_scenario = Execution()
    LOGGER.debug("[Fixture SETUP %s] ----   FIN   ----", fixture_name)

    yield execution_scenario

    LOGGER.debug("[Fixture FINAL %s] ----  DEBUT  ----", fixture_name)

    # Finalise le scénario après tous les tests
    execution_scenario.finalise()

    # Génération json et inscription
    nom_rapport_json = f"{execution_scenario.config.get('report_dir')}/scenario.json"
    json_execution = execution_scenario.save_to_json(nom_rapport_json)

    if execution_scenario.config.get("inscription"):
        inscrire_resultats_api(
            execution_scenario.config.get("url_base_api_injecteur"),
            json_execution,
        )
    else:
        LOGGER.warning(
            "[Fixture FINAL %s]⚠️ Scénario non inscrit en base (inscription = %s)",
            fixture_name,
            execution_scenario.config.get("inscription"),
        )
        LOGGER.info(
            "[Fixture FINAL %s] json scénario => \n  %s",
            fixture_name,
            json.dumps(json_execution, ensure_ascii=False, indent=4),
        )
    LOGGER.debug("[Fixture FINAL %s] ----   FIN   ----", fixture_name)
