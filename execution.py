"""
Execution - Contexte général de l'execution d'un test
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
from src.utils.recuperation_utilisateur import recuperer_utlisateur_isac
from .environnement import Environnement
from .configuration import Configuration
from src.utils.constantes import ConstantesSimulateur
from src.utils.planning_execution import verifier_planning_execution

# from src.utils.relance import relance

LOGGER = logging.getLogger(__name__)

# sympbole pour se reperer dans les logs !!! 🛑


class Execution:
    """Classe d'éxecution des scénarios"""

    def __init__(self) -> None:
        """
        Initialise l'execution un scénario avec un tableau d'étapes vide et charge la configuration.
        """
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)
        self.date = (datetime.now().isoformat(),)
        self.duree = 0
        # UNKNOWN par défaut
        self.status = 3
        self.commentaire = ""
        self.injecteur = ""
        self.navigateur = ""
        self.interface_ip = ""
        self.status_initial = ""
        self.commentaire_initial = ""
        self.etapes = []

        self.url_initiale_header = ""

        # TODO : Ajouter le nom de l'application et du scénarios que si disponibles

        # Liste des éléments à flouter
        self.elts_flous = []

        # Création d'un dictionnaire vide pour accueillir les données d'environnement
        self.environnement = {}

        # Initialisation de l'environnement
        self._get_environnement()

        # Création d'un dictionnaire vide pour accueillir les données API
        self.donnees_scenario_api = {}

        # Initialisation des données API
        self._get_donnees_scenario_api()

        # Vérification du planning d'exection
        self._verifier_planing()

        # Chargement de la configuration & compteur d'étapes
        self.config = {}

        # Initialisation de la configuration de l'execution
        self.get_config()

        # Création des répertoires de sorties
        self.gestion_repertoires_sortie()

        if self.config["type_scenario"] == ConstantesSimulateur.TYPE_SCENARIO_EXADATA:
            self.chemin_image_exadata()

        self.compteur_etape = 0

        LOGGER.debug("[%s] ----  FIN  ----", methode_name)

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
    status_inital : {self.status_initial}
    commentaire_initial : {self.commentaire_initial}
    etapes : {self.etapes}
    config : {self.config}
"""

    def _get_environnement(self):
        """Lecture des paramètres d'environnement."""
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        try:
            self.environnement.update(Environnement().charger_variables_environnement())
        except Exception as erreur_envrionnement:
            LOGGER.fatal(
                "[%s] Une erreur est survenue lors de la création de l'environnement : %s",
                methode_name,
                erreur_envrionnement,
            )

        LOGGER.debug("[%s] environnement => %s", methode_name, self.environnement)
        LOGGER.debug("[%s] ----  FIN  ----", methode_name)

    def _get_donnees_scenario_api(self):
        """
        Chargement des données de l'api de LECTURE pour completer la
        configuration si la variable d'environnement
        LECTURE n'est pas false.

        Args: None

        Returns:
            dict: données de l'API

        """
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        donnees_scenario_api = {}
        try:
            # Gestion du paramètre de lecture de l'API
            if not self.environnement.get("lecture", True):
                LOGGER.info(
                    "[%s] Lecture API désactivé => %s",
                    methode_name,
                    self.environnement.get("lecture"),
                )

                if self.environnement.get("plateforme") == "prod":
                    LOGGER.warning(
                        "[%s] ⚠️ Sorties désactivées : environnement prod et lecture API OFF",
                        methode_name,
                    )
            else:
                # Mise à jour du dictionnaire des données API
                self.donnees_scenario_api.update(
                    lecture_api_scenario(
                        url_base_api_injecteur=self.environnement[
                            "url_base_api_injecteur"
                        ],
                        identifiant_scenario=self.environnement["identifiant"],
                    )
                )
                LOGGER.info(
                    "[%s] api => %s",
                    donnees_scenario_api.get("nom"),
                    donnees_scenario_api,
                )

        except Exception as erreur_donnees_scenario_api:
            LOGGER.fatal(
                "[%s] Une erreur est survenue lors du chargement des données API : %s",
                methode_name,
                erreur_donnees_scenario_api,
            )
            pytest.exit()

        # TODO : Controle des parametres
        LOGGER.debug("[%s] ----  FIN  ---- ", methode_name)

    def _verifier_planing(self):
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        if self.environnement.get("lecture"):
            try:
                LOGGER.debug(
                    "[%s] DONNÉES API : %s ", methode_name, self.donnees_scenario_api
                )

                verifier_planning_execution(self.donnees_scenario_api)
                LOGGER.info(
                    "[%s] Planning d'exécution validé - Poursuite du traitement",
                    methode_name,
                )
            except SystemExit:
                # La fonction verifier_planning_execution a appelé pytest.exit(2)
                # On laisse l'exception remonter pour arrêter immédiatement
                LOGGER.info(
                    "[%s] Arrêt immédiat suite à violation du planning", methode_name
                )
                raise
            except Exception as e:
                # Erreur inattendue lors de la vérification du planning
                LOGGER.critical(
                    "[%s] Erreur critique lors de la vérification du planning: %s",
                    methode_name,
                    e,
                )
                print(f"Erreur critique lors de la vérification du planning: {e}")
                pytest.exit()

    def get_config(self) -> dict:
        """
        Chargement de la configuration du scénario à partir
        de sa configuration et des paramètres d'environnement
        Le fonction  fait un appel à l'api pour completer la
        configuration si la variable d'environnement
        LECTURE n'est pas false.

        Args: None

        Returns:
            dict: configuration du scenario pouur l'execution

        Note: Le chargement de la configration est effectué à partir
        de la variable d'environnement NOM_SCENARIO

        """
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        try:
            self.environnement.update(
                Configuration(environnement=self.environnement).creer_configuration()
            )
        except Exception as erreur_envrionnement:
            LOGGER.fatal(
                "[%s] Une erreur est survenue lors de la création de la configuration : %s",
                methode_name,
                erreur_envrionnement,
            )

        LOGGER.debug("[%s] environnement => %s", methode_name, self.environnement)
        LOGGER.debug("[%s] ----  FIN  ----", methode_name)

    def chemin_image_exadata(self):
        """Ajout du chemin des images exadata si le scénario est un exadata."""
        # Chemin des images à lire pour les scénarios exadata (CHEMIN_IMAGES_EXADATA)
        self.config["chemin_images_exadata"] = (
            f"{self.environnement.get("scenarios_path")}/scenarios_exadata/images/{self.config["nom_scenario"]}"
        )

    def gestion_repertoires_sortie(self):
        """
        Crée les répertoires de screenshots et de rapports.

        Args:
            configuration (dict): Dictionnaire contenant les chemins de sortie,
                                le nom du scénario, etc.

        Returns:
            None
        """
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        # Récupération de self.date (date et heur du lancement)
        # au format isoformat et conversion en objet datetime
        # pour pouvoir le manipuler extraire l'heure et la date
        date_heure = datetime.strptime(self.date[0], "%Y-%m-%dT%H:%M:%S.%f")
        date = date_heure.date()
        heure = date_heure.strftime("%H:%M:%S")

        # Configuration des répertoires screenshot et rapports avec les données API
        if self.donnees_scenario_api:
            nom_app = self.donnees_scenario_api.get("application").get("nom", False)
            nom_scenario = self.donnees_scenario_api.get("nom", False)
            LOGGER.info(
                "[%s] Chemin des répertoires construits avec les données API",
                methode_name,
            )
            self.config["screenshot_dir"] = (
                f"{self.config['output_path']}/screenshots/{nom_app}/{nom_scenario}/{date}/{heure}"
            )
            self.config["report_dir"] = (
                f"{self.config['output_path']}/rapports/{nom_app}/{nom_scenario}/{date}/{heure}"
            )
        else:
            # Configuration des répertoires screenshot et rapports avec les données de configuration
            LOGGER.info(
                "[%s] Chemin des répertoires construits avec la configuration",
                methode_name,
            )
            self.config["screenshot_dir"] = (
                f"{self.config['output_path']}/screenshots/NO_API/{self.config['nom_scenario']}/{date}/{heure}"
            )
            self.config["report_dir"] = (
                f"{self.config['output_path']}/rapports/NO_API/{self.config['nom_scenario']}/{date}/{heure}"
            )

        # Création des réperoires screenshot et rapports
        try:
            LOGGER.info("[%s] Création des répertoires", methode_name)
            Path(self.config["screenshot_dir"]).mkdir(parents=True, exist_ok=True)
            Path(self.config["report_dir"]).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            LOGGER.warning(
                "[%s]⚠️ Impossible de créer les répertoires de screenshot et rapports\n%s",
                methode_name,
                e,
            )
            LOGGER.warning(
                "[%s]⚠️ Les screenshots et rapports ne seront pas générés", methode_name
            )
            self.config["screenshot_dir"] = None
            self.config["report_dir"] = None

        LOGGER.debug(
            "[%s] screenshot_dir => %s", methode_name, self.config["screenshot_dir"]
        )
        LOGGER.debug("[%s] report_dir => %s", methode_name, self.config["report_dir"])
        LOGGER.debug("[%s] ----  FIN  ----", methode_name)

    def _get_params(self) -> dict:
        """TODO: Pas encore implémentée."""
        return {}

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

        # TODO : Mettre ce code dans une methode dédiée
        self.duree = sum([float(etape["duree"]) for etape in self.etapes])

        # Cumul seulement si il y a des étapes
        if len(self.etapes) > 0:
            self.status = self.etapes[-1]["status"]
            LOGGER.debug(
                "[%s] self.status => %s ", methode_name, self.etapes[-1]["status"]
            )
            self.status_initial = self.etapes[-1]["status"]
            LOGGER.debug(
                "[%s] self.status_initial => %s ",
                methode_name,
                self.etapes[-1]["status"],
            )
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
            "date": self.date[0],
            "duree": self.duree,
            "status": self.status,
            "nb_scene": len(self.etapes),
            "commentaire": self.commentaire,
            "injecteur": self.injecteur,
            "navigateur": self.navigateur,
            "interface_ip": self.interface_ip,
            "status_inital": self.status_initial,
            "commentaire_initial": self.commentaire_initial,
            "briques": self.etapes,
        }
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        LOGGER.debug("[%s] ----  FIN  ----", methode_name)
        return data


@pytest.fixture(scope="session")
def execution():
    """Crée un scénario unique pour tous les tests et le finalise à la fin."""
    fixture_name = contexte_actuel()
    LOGGER.debug("[Fixture SETUP %s] ----  DEBUT  ----", fixture_name)

    execution_scenario = Execution()
    LOGGER.debug("[Fixture SETUP %s] ----   FIN   ----", fixture_name)

    # Retourne l'instance du scénario pour tous les tests
    yield execution_scenario

    LOGGER.debug("[Fixture FINAL %s] ----  DEBUT  ----", fixture_name)

    # TODO : Ajouter la relance automatique

    # # Si relance est True alors on relance le scénario
    # if relance(
    #     url_base_api_injecteur=execution_scenario.config.get("url_base_api_injecteur"),
    #     identifiant=execution_scenario.config.get("identifiant"),
    # ) and os.environ["RELANCE"] == 'true':
    #     LOGGER.debug("[%s] ---- RELANCE AUTO ----", fixture_name)
    #     # TODO : Supprimer les screenshots du rejeu KO

    #     # Mise à jour de la variable d'environnement de relance
    #     os.environ["RELANCE"] = 'false'

    #     # Préparer les arguments pour le nouveau processus
    #     original_args = sys.argv.copy()

    #     env = os.environ.copy()

    #     processes = [
    #         'playwright'
    #     ]

    #     for process_name in processes:
    #         subprocess.run(
    #             ['pkill', '-f', process_name],
    #             capture_output=True,
    #             check=False
    #         )

    #     subprocess.run(
    #         original_args,
    #         env=env,
    #         capture_output=False,
    #         check=False
    #     )

    # # Sinon on finalise la création du rapport json
    # else:
    # Finalise le scénario après tous les tests
    execution_scenario.finalise()

    # generation json (et ecriture sur dans les rapports)
    nom_rapport_json = f"{execution_scenario.config.get('report_dir')}/scenario.json"
    json_execution = execution_scenario.save_to_json(nom_rapport_json)

    # et inscription
    if execution_scenario.config.get("inscription"):
        inscrire_resultats_api(
            execution_scenario.config.get("url_base_api_injecteur"),
            json_execution,
        )
    else:
        # ou dump du json
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
