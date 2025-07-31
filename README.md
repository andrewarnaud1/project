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
        self.environnement = self._get_environnement()

        # Création d'un dictionnaire vide pour accueillir les données API
        self.donnees_scenario_api = self.creer_donnees_scenario_api()

        # Chargement de la configuration & compteur d'étapes
        self.config = self.creer_config()

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

    def creer_donnees_scenario_api(self) -> dict:
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
            donnees_scenario_api = lecture_api_scenario(
                url_base_api_injecteur=self.config["url_base_api_injecteur"],
                identifiant_scenario=self.config["identifiant"],
            )
            # LOGGER.info('[%s] --- Données API ---', configuration['scenario'])
            LOGGER.info(
                "[%s] api => %s", donnees_scenario_api.get("nom"), donnees_scenario_api
            )
            
        # TODO Controle des parametres
        LOGGER.debug("[%s] ----  FIN  ---- ", methode_name)
        return donnees_scenario_api
    

    def creer_config(self) -> dict:
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
        de la variable d'environnement SCENARIO

        """
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        params = self._get_params()
        environnement = self.environnement

        # Lecture du fichier de configuration du scenario
        configuration = {}
        config_path = f"{environnement['simu_scenarios']}/config/scenarios/{environnement['scenario']}.conf"
        try:
            configuration = load_yaml_file(config_path)
        except Exception as e:
            LOGGER.fatal(
                "[%s]❌ Impossible de lire le fichier de configuration du scenario\n%s",
                methode_name,
                e,
            )
            pytest.exit()

        # Lecture de la configuration brique commune si définie
        if "config_commune" in configuration.keys():
            config_commune_path = f"{environnement['simu_scenarios']}/config/commun/{configuration['config_commune']}.conf"
            try:
                configuration_commune = load_yaml_file(config_commune_path)
            except Exception as e:
                LOGGER.fatal(
                    "[%s]❌ Impossible de lire le fichier de configuration de l'etape commune\n%s",
                    methode_name,
                    e,
                )
                pytest.exit(2)
            configuration = configuration | configuration_commune

        # Gestion des paramètres url, proxy, navigateur
        configuration["url_initiale"] = self._get_url_initiale(
            configuration, environnement
        )
        configuration["proxy"] = self._get_proxy(configuration, environnement)
        configuration["navigateur"] = self._get_navigateur(configuration, environnement)

        # TODO Aggregation paramètres (Pas encore implémenté)
        configuration = environnement | configuration

        # Indicateur pour désactiver screenshots et rapports
        # activer_sorties = True

        if self.donnees_scenario_api:
            configuration["scenario"] = self.donnees_scenario_api.get("nom")
            LOGGER.info(
                "[%s] api => %s", configuration["scenario"], self.donnees_scenario_api
            )

        self.gestion_repertoires_sortie(configuration)

        if "utilisateur_isac" in configuration.keys():
            # Si la variable utilisateur_isac est présente dans les clés de la configuration
            # il faut récupérer les données présente dans le fichier
            utilisateur_isac = self._get_utilisateur_isac(configuration)
            configuration = configuration | utilisateur_isac

        # Simplification des dictionnaires par plateforme
        for cle, valeur in list(configuration.items()):
            if isinstance(valeur, dict) and configuration["plateforme"] in valeur:
                configuration[cle] = valeur[configuration["plateforme"]]
                LOGGER.debug(
                    "[%s] %s simplifié pour %s => %s",
                    methode_name,
                    cle,
                    configuration["plateforme"],
                    configuration[cle],
                )

        # Chemin des images à lire pour les scénarios exadata (CHEMIN_IMAGES_EXADATA)
        configuration["chemin_images_exadata"] = f"{environnement.get("simu_scenarios")}/scenarios_exadata/images/{configuration["scenario"]}"

        # Affichage de la configuration
        LOGGER.info("[%s] --- Configuration ---", configuration["scenario"])
        LOGGER.info(
            "[%s] navigateur => %s",
            configuration["scenario"],
            configuration["navigateur"],
        )
        LOGGER.info(
            "[%s] plateforme => %s",
            configuration["scenario"],
            configuration["plateforme"],
        )
        LOGGER.info(
            "[%s] url_initiale => %s",
            configuration["scenario"],
            configuration["url_initiale"],
        )
        LOGGER.info(
            "[%s] proxy => %s", configuration["scenario"], configuration["proxy"]
        )
        LOGGER.info(
            "[%s] simu_path => %s",
            configuration["scenario"],
            configuration["simu_path"],
        )
        LOGGER.info(
            "[%s] simu_scenarios => %s",
            configuration["scenario"],
            configuration["simu_scenarios"],
        )
        LOGGER.info(
            "[%s] simu_output => %s",
            configuration["scenario"],
            configuration["simu_output"],
        )
        LOGGER.info(
            "[%s] headless => %s", configuration["scenario"], configuration["headless"]
        )
        LOGGER.info(
            "[%s] lecture => %s", configuration["scenario"], configuration["lecture"]
        )
        LOGGER.info(
            "[%s] inscription => %s",
            configuration["scenario"],
            configuration["inscription"],
        )

        LOGGER.info(
            "[%s] screenshot_dir => %s",
            configuration["scenario"],
            configuration["screenshot_dir"],
        )
        LOGGER.info(
            "[%s] report_dir => %s",
            configuration["scenario"],
            configuration["report_dir"],
        )

        if "utilisateur" in configuration.keys():
            LOGGER.debug(
                "[%s] utilisateur => %s",
                configuration["scenario"],
                configuration["utilisateur"],
            )
        if "mot_de_passe" in configuration.keys():
            LOGGER.debug(
                "[%s] mot_de_passe => %s",
                configuration["scenario"],
                configuration["mot_de_passe"],
            )

        # TODO Controle des parametres
        LOGGER.debug("[%s] => %s ----  FIN  ---- ", methode_name, configuration)
        return configuration

    def gestion_repertoires_sortie(self, configuration):
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
            configuration["screenshot_dir"] = (
                f"{configuration['simu_output']}/screenshots/{nom_app}/{nom_scenario}/{date}/{heure}"
            )
            configuration["report_dir"] = (
                f"{configuration['simu_output']}/rapports/{nom_app}/{nom_scenario}/{date}/{heure}"
            )
        else:
            # Configuration des répertoires screenshot et rapports avec les données de configuration
            LOGGER.info(
                "[%s] Chemin des répertoires construits avec la configuration",
                methode_name,
            )
            configuration["screenshot_dir"] = (
                f"{configuration['simu_output']}/screenshots/NO_API/{configuration['scenario']}/{date}/{heure}"
            )
            configuration["report_dir"] = (
                f"{configuration['simu_output']}/rapports/NO_API/{configuration['scenario']}/{date}/{heure}"
            )

        # Création des réperoires screenshot et rapports
        try:
            LOGGER.info("[%s] Création des répertoires", methode_name)
            Path(configuration["screenshot_dir"]).mkdir(parents=True, exist_ok=True)
            Path(configuration["report_dir"]).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            LOGGER.warning(
                "[%s]⚠️ Impossible de créer les répertoires de screenshot et rapports\n%s",
                methode_name,
                e,
            )
            LOGGER.warning(
                "[%s]⚠️ Les screenshots et rapports ne seront pas générés", methode_name
            )
            configuration["screenshot_dir"] = None
            configuration["report_dir"] = None

        LOGGER.debug(
            "[%s] screenshot_dir => %s", methode_name, configuration["screenshot_dir"]
        )
        LOGGER.debug("[%s] report_dir => %s", methode_name, configuration["report_dir"])
        LOGGER.debug("[%s] ----  FIN  ----", methode_name)

    def _get_params(self) -> dict:
        """TODO: Pas encore implémentée."""
        return {}

    def _get_utilisateur_isac(self, configuration) -> dict:
        """Décodage deu fichier utilisateur."""
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        utilisateur = recuperer_utlisateur_isac(configuration)

        LOGGER.debug("[%s] environnement => %s", methode_name, utilisateur)
        LOGGER.debug("[%s] ----  FIN  ----", methode_name)
        return utilisateur

    def _get_environnement(self) -> dict:
        """Lecture des paramètres d'environnement."""
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        environnement = {}

        # la variable d'environnement SCENARIO est obligatoire
        environnement["scenario"] = os.environ.get("SCENARIO")
        if not environnement["scenario"]:
            LOGGER.fatal("[%s]❌ Variable d'environnement SCENARIO non definie.")
            pytest.exit(2)

        LOGGER.info("Scenario [%s] ---- DEBUT ----", environnement["scenario"])

        # Vérification du navigateur => TODO A mettre dans une methode dédiée
        if "BROWSER" in os.environ:
            environnement["navigateur"] = os.getenv("BROWSER")
            LOGGER.info(
                "[%s] Navigateur fixé par l'environnement : %s",
                environnement["scenario"],
                environnement["navigateur"],
            )

        environnement["simu_path"] = os.environ.get("SIMU_PATH", "/opt/simulateur_v6")
        environnement["simu_scenarios"] = os.getenv(
            "SIMU_SCENARIOS", "/opt/scenarios_v6"
        )
        environnement["path_utilisateurs_isac"] = os.environ.get(
            "PATH_UTILISATEURS_ISAC", "/opt/simulateur_v6"
        )
        environnement["simu_output"] = os.environ.get(
            "SIMU_OUTPUT", "/var/simulateur_v6"
        )

        # TODO Gestion optionnelle de la lecture et de l'inscription avec l'API
        environnement["url_base_api_injecteur"] = os.environ.get(
            "URL_BASE_API_INJECTEUR", "http://localhost/"
        )
        environnement["plateforme"] = os.environ.get("PLATEFORME", "prod")
        environnement["proxy"] = os.getenv("PROXY")

        # Gestion du paramètre de lecture
        lecture_env = os.getenv("LECTURE", "true").lower()
        # environnement['lecture'] sera True pour toute valeur de LECTURE autre que 'false'
        environnement["lecture"] = lecture_env != "false"

        # Explication des paramètres
        # Si 'lecture' est False, alors 'inscription' est False
        # Si 'lecture' est True (par défaut), alors 'inscription' peut être
        # désactivée en la mettant à False (par défaut, c'est True aussi)
        inscription_env = os.getenv("INSCRIPTION", "true").lower()
        environnement["inscription"] = (
            environnement["lecture"] and inscription_env != "false"
        )

        # Pareil pour le headless, il est descativé seulement avec HEADLESS = False
        headless_env = os.getenv("HEADLESS", "true").lower()
        environnement["headless"] = headless_env != "false"

        # Emplacement des binaires des navigateurs playwright
        environnement["playwright_browsers_path"] = os.getenv(
            "PLAYWRIGHT_BROWSERS_PATH", environnement["simu_path"] + "/browsers"
        )

        # Nom de la VM à démarrer sur Guacamole (SCENARIO_EXADATA)
        environnement["nom_vm_windows"] = os.getenv(
            "NOM_VM_WINDOWS", ''
        )

        LOGGER.debug("[%s] environnement => %s", methode_name, environnement)
        LOGGER.debug("[%s] ----  FIN  ----", methode_name)
        return environnement

    def _get_url_initiale(self, configuration, environnement) -> str:
        """retourne l'url initiale en écrasant le dictionnaire url_initiale
        (simplification du code pour le scénario).
        """
        # url initiale (obligatoire) = celle de la plateforme
        if "url_initiale" not in configuration.keys():
            LOGGER.critical(
                re.sub(
                    r"^\s+",
                    "",
                    f"""Aucune url_initiale définie dans le configuration du scénario ou des etapes communes
                |url_initiale :
                |    {environnement['plateforme']}: "https://www.exemple.net"
                """,
                    flags=re.MULTILINE,
                )
            )
            pytest.exit(2)
        if environnement["plateforme"] not in configuration["url_initiale"].keys():
            LOGGER.critical(
                re.sub(
                    r"^\s+",
                    "",
                    f"""Aucune url_initiale pour l'envionnement [{environnement['plateforme']}] n'est définie dans le configuration du scénario ou des etapes communes
                |url_initiale :
                |    {environnement['plateforme']}: "https://www.exemple.net"
                """,
                    flags=re.MULTILINE,
                )
            )
            pytest.exit(2)
        url_initiale = configuration["url_initiale"][environnement["plateforme"]]
        del configuration["url_initiale"]
        return url_initiale

    def _get_proxy(self, configuration, environnement) -> str:
        """Retourne la configuration du proxy."""
        # Valeur par défaut ('')
        proxy = ""

        # Le proxy via l'environnement est prioritaire sur la configuration
        if environnement["proxy"] is not None:
            proxy = environnement["proxy"]
            del environnement["proxy"]
        else:
            # Configuration du scénario (si elle existe)
            if "proxy" in configuration.keys():
                if environnement["plateforme"] not in configuration["proxy"].keys():
                    proxy = ""
                    LOGGER.warning(
                        "[%s] proxy est défini mais par pour la plateforme, => proxy direct"
                    )
                else:
                    proxy = configuration["proxy"][environnement["plateforme"]]
                del configuration["proxy"]

        return proxy

    def _get_navigateur(self, configuration, environnement) -> str:
        """Retourne le navigateur utilisé pour le test."""
        methode_name = contexte_actuel(self)
        # si le navigateur est defini dans l'environnement on prend
        if "navigateur" in environnement.keys():
            navigateur = environnement["navigateur"]
            del environnement["navigateur"]
        else:
            # Sinon dans la conf du scenario sinon firefox
            navigateur = configuration.get("navigateur", "firefox")
        LOGGER.debug("[%s]  -> %s ", methode_name, navigateur)
        return navigateur

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
            "scenario": self.config.get("scenario", ""),
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

    if execution_scenario.config.get('lecture'):
        try:
            verifier_planning_execution(execution_scenario.donnees_scenario_api)
            LOGGER.info("[%s] ✅ Planning d'exécution validé - Poursuite du traitement", fixture_name)
        except SystemExit:
            # La fonction verifier_planning_execution a appelé pytest.exit(2)
            # On laisse l'exception remonter pour arrêter immédiatement
            LOGGER.info("[%s] 🛑 Arrêt immédiat suite à violation du planning", fixture_name)
            raise
        except Exception as e:
            # Erreur inattendue lors de la vérification du planning
            LOGGER.critical("[%s] ❌ Erreur critique lors de la vérification du planning: %s", 
                        fixture_name, e)
            print(f"❌ Erreur critique lors de la vérification du planning: {e}")
            pytest.exit(2)

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

