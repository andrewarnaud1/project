"""
Module Configuration - Gestionnaire des variables de configuration

Ce module centralise la lecture et la validation des variables de configuration.

Classes:
--------
- Configuration : Classe principale pour la gestion des variables d'environnement

Fonctionnalités:
---------------
- Lecture des fichiers de configuration du scénario et configuration commune
avec valeurs par défaut
- Validation des variables obligatoires
- Gestion des erreurs avec messages explicites

Exemple d'utilisation:
---------------------
>>> from src.utils.configuration import Configuration
>>>
>>> environnement = Configuration().charger_configuration()
>>> print(configuration[''])

Variables :
------------------------------------

"""


from typing import Dict, Any
import logging
from src.utils.utils import contexte_actuel
from src.utils.booleen import convertir_booleen
from src.utils.recuperation_utilisateur import recuperer_utlisateur_isac
from src.utils.constantes import ConstantesSimulateur
from src.utils import load_yaml_file

LOGGER = logging.getLogger(__name__)


class Configuration:
    """
    Gestionnaire des variables d'environnement pour l'exécution des scénarios.

    Cette classe centralise la lecture, la validation et la conversion
    des variables d'environnement nécessaires au bon fonctionnement
    du simulateur de tests automatisés.
    """

    def __init__(self, environnement: dict):
        """
        Initialise le gestionnaire des variables d'environnement.
        """
        # Liste des variables obligatoires
        self.variables_obligatoires = []

        self.environnement = environnement

        # Chargement des variables
        self.configuration_scenario = self._get_config_scenario()

        # Chargement des variables
        self.configuration_commune = self._get_config_commune()

    def _get_config_scenario(self):
        """Méthode pour obtenir les données de la configuration du scénario"""
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        config_path = f"{self.environnement['scenarios_path']}/config/scenarios/{self.environnement['nom_scenario']}.conf"

        try:
            configuration_scenario = load_yaml_file(config_path)
        except Exception as e:
            LOGGER.fatal(
                "[%s]❌ Impossible de lire le fichier de configuration du scenario\n%s",
                methode_name,
                e,
            )

        LOGGER.debug("[%s] ----  FIN  ---- ", methode_name)

        return configuration_scenario

    def _get_config_commune(self):
        """Méthode pour obtenir les données de la configuration commune du scénario."""
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        # Lecture de la configuration brique commune si définie
        if "config_commune" in self.configuration_scenario.keys():
            config_commune_path = f"{self.environnement['scenarios_path']}/config/commun/{self.configuration_scenario['config_commune']}.conf"
            try:
                configuration_commune = load_yaml_file(config_commune_path)
            except Exception as e:
                LOGGER.fatal(
                    "[%s]❌ Impossible de lire le fichier de configuration commune\n%s",
                    methode_name,
                    e,
                )

        LOGGER.debug("[%s] ----  FIN  ---- ", methode_name)

        return configuration_commune

    def creer_configuration(self) -> Dict[str, Any]:
        """
        Construit le dictionnaire de configuration à partir des fichiers de configuration.

        Returns: Dictionnaire contenant toutes les variables de configuration
        """
        methode_name = contexte_actuel(self)
        LOGGER.info("[%s] ---- DEBUT ----", methode_name)

        configuration = {}

        # Ajout des variables au dictionnaire
        configuration.update(self.configuration_scenario)
        configuration.update(self.configuration_commune)

        # On garde seulement les variables qui concernent la plateforme actuelle
        configuration = self._recuperation_variables_plateforme(dictionnaire=configuration)

        # Mise à jour du dictionnaire avec les variables d'environnement
        # Les variables de l'envrionnement écrase les valeurs du fichier
        # de configuration
        configuration.update(self.environnement)

        # Ajout de l'utilisateur à la configuration
        if "utilisateur_isac" in configuration.keys():
            # Si la variable utilisateur_isac est présente dans les clés de la configuration
            # il faut récupérer les données présente dans le fichier
            utilisateur_isac = recuperer_utlisateur_isac(configuration)
            configuration.update(utilisateur_isac)

        # # Traitement des variables obligatoires
        # self._verification_variables_obligatoires(
        #     self.variables_obligatoires, environnement=environnement
        # )

        LOGGER.info("[%s] configuration finale => %s", methode_name, configuration)
        LOGGER.info("[%s] ----  FIN  ----", methode_name)
        return configuration

    def _recuperation_variables_plateforme(self, dictionnaire) -> dict:
        """
        Permets de récupérer uniquement les variables de la plateforme utilisée.

        Return: un dictionnaire avec les variables de la plateforme seulement.
        """
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        # Simplification des dictionnaires par plateforme
        for cle, valeur in list(dictionnaire.items()):
            if isinstance(valeur, dict) and self.environnement["plateforme"] in valeur:
                dictionnaire[cle] = valeur[self.environnement["plateforme"]]
                LOGGER.debug(
                    "[%s] %s simplifié pour %s => %s",
                    methode_name,
                    cle,
                    self.environnement["plateforme"],
                    dictionnaire[cle],
                )

        LOGGER.debug("[%s] ----  FIN  ----", methode_name)

        return dictionnaire

    # def _verification_variables_obligatoires(
    #     self, variables_obligatoire: list, environnement: dict
    # ):
    #     """
    #     Charge et valide toutes les variables d'environnement nécessaires.
    #     """

    #     methode_name = contexte_actuel(self)
    #     LOGGER.info("[%s] ---- DEBUT ----", methode_name)

    #     for variable in variables_obligatoire:
    #         LOGGER.info("%s", variable)
    #         if variable not in environnement.keys() or environnement[variable] is None:
    #             LOGGER.fatal(
    #                 "[%s] ❌ Variable %s non définie.",
    #                 methode_name,
    #                 variable,
    #             )
    #             raise ValueError(f"Variable d'environnement {variable} non définie.")

    #     LOGGER.info("[%s] ----  FIN  ----", methode_name)