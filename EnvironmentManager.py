"""
Module EnvironmentManager - Gestionnaire des variables d'environnement

Ce module centralise la lecture et la validation des variables d'environnement
nécessaires à l'exécution des scénarios de test automatisés.

Classes:
--------
- EnvironmentManager : Classe principale pour la gestion des variables d'environnement

Fonctionnalités:
---------------
- Lecture des variables d'environnement avec valeurs par défaut
- Validation des variables obligatoires
- Gestion des erreurs avec messages explicites

Exemple d'utilisation:
---------------------
>>> from src.utils.environment_manager import EnvironmentManager
>>>
>>> manager = EnvironmentManager()
>>> environnement = manager.charger_variables_environnement()
>>> print(environnement['scenario'])  # Nom du scénario
>>> print(environnement['headless'])  # True/False

Variables d'environnement :
------------------------------------
- SCENARIO: Nom du scénario à exécuter
- NAVIGATEUR : Navigateur à utiliser (firefox, chromium, msedge)
- PLATEFORME : Environnement d'exécution (dev, test, prod)
- HEADLESS : Mode sans interface graphique (true/false)
- LECTURE : Activation de la lecture API (true/false)
- INSCRIPTION : Activation de l'inscription API (true/false)
- PROXY : Configuration du proxy
- SIMU_PATH : Chemin d'installation du simulateur
- SCENARIOS_PATH : Chemin des scénarios
- OUTPUT_PATH : Chemin de sortie des rapports
- URL_BASE_API_INJECTEUR : URL de base de l'API
- PATH_UTILISATEURS_ISAC : Chemin des fichiers utilisateurs
- PLAYWRIGHT_NAVIGATEURS_PATH : Chemin des navigateurs Playwright
- NOM_VM_WINDOWS : Nom de la VM Windows pour Guacamole
"""

import os
from typing import Dict, Any
import logging
import pytest
from src.utils.utils import contexte_actuel
from src.utils.booleen import convertir_booleen
from src.utils.constantes import ConstantesSimulateur

LOGGER = logging.getLogger(__name__)


class Environnement:
    """
    Gestionnaire des variables d'environnement pour l'exécution des scénarios.

    Cette classe centralise la lecture, la validation et la conversion
    des variables d'environnement nécessaires au bon fonctionnement
    du simulateur de tests automatisés.
    """

    def __init__(self):
        """
        Initialise le gestionnaire des variables d'environnement.
        """
        self.variables_obligatoires = [
            "simu_path",
            "scenarios_path",
            "output_path",
            "playwright_browsers_path",
            "utilisateur_isac_path",
            "scenario",
        ]

        self.nom_scenario = self._charger_nom_scenario()
        self.chemins = self._charger_chemins()
        self.variables_interaction_api = self._charger_variables_interaction_api()
        self.type_scenario = self._charger_type_scenario()
        self.parametres_navigateur = self._charger_parametres_navigateur()
        self.plateforme = self._charger_plateforme()
        self.type_scenario = self._charger_type_scenario()
        self.nom_vm_windows = None

        # Si on a un scénario de type EXADATA il faut charger le nom de la VM
        if self.type_scenario == "EXADATA":
            self.nom_vm_windows = self._charger_nom_vm_windows()
            # Mettre à jour la liste des variables obligatoires
            self.variables_obligatoires.append(self.nom_vm_windows)

    def charger_variables_environnement(self) -> Dict[str, Any]:
        """
        Construit le dictionnaire des variables d'environnement.

        Returns:
            Dict[str, Any]: Dictionnaire contenant toutes les variables d'environnement
                            avec leurs valeurs
        """
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        environnement = {}

        # Ajout des variables au dictionnaire
        environnement.update(
            self.nom_scenario,
            self.chemins,
            self.variables_interaction_api,
            self.type_scenario,
            self.parametres_navigateur,
            self.plateforme,
            self.type_scenario,
            self.nom_vm_windows,
        )

        # Traitement des variables obligatoires
        self._verification_variables_obligatoires(
            self.variables_obligatoires, environnement=environnement
        )

        LOGGER.debug("[%s] environnement => %s", methode_name, environnement)
        LOGGER.debug("[%s] ----  FIN  ----", methode_name)
        return environnement

    def _verification_variables_obligatoires(
        self, variables_obligatoire: list, environnement: dict
    ):
        """
        Charge et valide toutes les variables d'environnement nécessaires.
        """

        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

        for variable in variables_obligatoire:
            if variable not in environnement.keys():
                LOGGER.fatal(
                    "[%s] ❌ Variable d'environnement %s non définie.",
                    methode_name,
                    variable,
                )
                pytest.exit(2)

        # TODO : Raise une erreur

        LOGGER.debug("[%s] ----  FIN  ----", methode_name)

    def _charger_nom_scenario(self) -> str:
        """
        Récupère le nom du scénario à partir de l'environnement.

        Returns:
            str: Nom du scénario
        """

        return os.getenv("NOM_SCENARIO", None)

    def _charger_chemins(self) -> dict:
        """
        Récupère les différents chemin de nécessaire pour l'execution :

        - SIMU_PATH : Chemin d'installation du simulateur
        - SCENARIOS_PATH : Chemin des scénarios
        - OUTPUT_PATH : Chemin de sortie des rapports
        - URL_BASE_API_INJECTEUR : URL de base de l'API
        - PATH_UTILISATEURS_ISAC : Chemin des fichiers utilisateurs
        - PLAYWRIGHT_NAVIGATEURS_PATH : Chemin des navigateurs Playwright

        Returns:
            dict: Variables des chemin de sorties, de répertoires des scénarios et des navigateurs
        """

        chemins = {}

        chemins["simu_path"] = os.getenv("SIMU_PATH", "/opt/simulateur_v6")
        chemins["scenarios_path"] = os.getenv("SCENARIOS_PATH", "/opt/scenarios_v6")
        chemins["output_path"] = os.getenv("OUTPUT_PATH", "/opt/scenarios_v6")
        chemins["playwright_browsers_path"] = os.getenv(
            "PLAYWRIGHT_NAVIGATEURS_PATH", "/browsers"
        )
        chemins["utilisateur_isac_path"] = os.getenv(
            "UTILISATEURS_ISAC_PATH", "/opt/scenarios_v6/config/utilisateurs"
        )

        return chemins

    def _charger_variables_interaction_api(self) -> dict:
        """
        Récupère les variables d'environnement :
        - LECTURE
        - INSCRIPTION
        - URL_BASE_API_INJECTEUR

        Returns:
            dict: Variable d'activation des API's de LECTURE et ECRITURE et URL
        """

        variables_interaction_api = {}

        # LECTURE (défaut: true)
        lecture_env = os.getenv("LECTURE", "true").lower().strip()
        variables_interaction_api["lecture"] = convertir_booleen(lecture_env, "LECTURE")

        # INSCRIPTION (défaut: true, mais dépend de LECTURE)
        inscription_env = os.getenv("INSCRIPTION", "true").lower().strip()
        inscription_bool = convertir_booleen(inscription_env, "INSCRIPTION")
        # Si lecture est False, inscription est forcément False
        variables_interaction_api["inscription"] = (
            variables_interaction_api["lecture"] and inscription_bool
        )

        variables_interaction_api["url_base_api_injecteur"] = os.getenv(
            "URL_BASE_API_INJECTEUR", "http://localhost/"
        )

        return variables_interaction_api

    def _charger_parametres_navigateur(self) -> dict:
        """
        Charge les paramètres de configuration du navigateur.

        Returns:
            Dict[str, Any]: Paramètres navigateur

        Raises:
            ValueError: si navigateur invalide
        """
        parametres_navigateur = {}

        # NAVIGATEUR (défaut: firefox)
        navigateur = (
            os.getenv("NAVIGATEUR", ConstantesSimulateur.NAVIGATEUR_FIREFOX)
            .lower()
            .strip()
        )
        if navigateur not in ConstantesSimulateur.NAVIGATEURS_VALIDES:
            raise ValueError(
                f"NAVIGATEUR '{navigateur}' invalide. "
                f"Valeurs autorisées : {', '.join(ConstantesSimulateur.NAVIGATEURS_VALIDES)}",
            )
        parametres_navigateur["navigateur"] = navigateur

        # HEADLESS (défaut: true)
        headless_env = os.getenv("HEADLESS", "true").lower().strip()
        parametres_navigateur["headless"] = convertir_booleen(headless_env, "HEADLESS")

        # PROXY (optionnel)
        parametres_navigateur["proxy"] = os.getenv("PROXY", "").strip()

        LOGGER.debug(
            "[_charger_parametres_navigateur] Paramètres navigateur chargés : %s",
            list(parametres_navigateur.keys()),
        )
        return parametres_navigateur

    def _charger_plateforme(self) -> str:
        """
        Récupère la variable d'environnement PLATEFORME

        Returns:
            str:
        """

        # TODO : Faire appel au fichier de constantes
        return os.getenv("PLATEFORME", "prod")

    def _charger_type_scenario(self) -> str:
        """
        Récupère la variable d'environnement TYPE_SCENARIO

        Returns:
            str: Variable du type de scénario (WEB, EXADATA, TECHNIQUE)
        """

        return os.getenv("TYPE_SCENARIO", None)

    def _charger_nom_vm_windows(self) -> str:
        """
        Récupère la variable d'environnement NOM_VM_WINDOWS

        Returns:
            str:
        """

        # NOM_VM_WINDOWS
        # Si le type de scénario est exadata il faut appeler cette variable et elle est obligatoire sinon on arrête le scénario

        return os.getenv("NOM_VM_WINDOWS", None)
