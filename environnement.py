"""
Module Environnement - Gestionnaire des variables d'environnement

Ce module centralise la lecture et la validation des variables d'environnement
nécessaires à l'exécution des scénarios de test automatisés.

Classes:
--------
- Environnement : Classe principale pour la gestion des variables d'environnement

Fonctionnalités:
---------------
- Lecture des variables d'environnement avec valeurs par défaut
- Validation des variables obligatoires
- Gestion des erreurs avec messages explicites

Exemple d'utilisation:
---------------------
>>> from src.utils.environment import Environnement
>>>
>>> environnement = Environnement().charger_variables_environnement()
>>> print(environnement['nom_scenario'])  # Nom du scénario

Variables d'environnement :
------------------------------------
- NOM_SCENARIO: Nom du scénario à exécuter
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
        # Liste des variables obligatoires
        self.variables_obligatoires = [
            "nom_scenario",
            "type_scenario",
            "simu_path",
            "scenarios_path",
            "output_path",
            "playwright_browsers_path",
        ]

        # Chargement des variables
        self.nom_scenario = self._charger_nom_scenario()
        self.chemins = self._charger_chemins()
        self.variables_interaction_api = self._charger_variables_interaction_api()
        self.type_scenario = self._charger_type_scenario()
        self.parametres_navigateur = self._charger_parametres_navigateur()
        self.plateforme = self._charger_plateforme()
        self.type_scenario = self._charger_type_scenario()

    def charger_variables_environnement(self) -> Dict[str, Any]:
        """
        Construit le dictionnaire des variables d'environnement.

        Returns: Dictionnaire contenant toutes les variables d'environnement
                  avec leurs valeurs
        """
        methode_name = contexte_actuel(self)
        LOGGER.info("[%s] ---- DEBUT ----", methode_name)

        environnement = {}

        # Ajout des variables au dictionnaire
        environnement.update(self.nom_scenario)
        environnement.update(self.type_scenario)
        environnement.update(self.plateforme)
        environnement.update(self.chemins)
        environnement.update(self.variables_interaction_api)
        environnement.update(self.parametres_navigateur)

        # Si le scénario est de type EXADATA il faut charger le nom de la VM
        if environnement['type_scenario'] == ConstantesSimulateur.TYPE_SCENARIO_EXADATA:
            environnement.update(self._charger_nom_vm_windows())
            # Mettre à jour la liste des variables obligatoires
            self.variables_obligatoires.append('nom_vm_windows')

        # Traitement des variables obligatoires
        self._verification_variables_obligatoires(
            self.variables_obligatoires, environnement=environnement
        )

        LOGGER.info("[%s] environnement => %s", methode_name, environnement)
        LOGGER.info("[%s] ----  FIN  ----", methode_name)
        return environnement

    def _verification_variables_obligatoires(
        self, variables_obligatoire: list, environnement: dict
    ):
        """
        Charge et valide toutes les variables d'environnement nécessaires.
        """

        methode_name = contexte_actuel(self)
        LOGGER.info("[%s] ---- DEBUT ----", methode_name)

        for variable in variables_obligatoire:
            LOGGER.info("%s", variable)
            if variable not in environnement.keys() or environnement[variable] is None:
                LOGGER.fatal(
                    "[%s] ❌ Variable d'environnement %s non définie.",
                    methode_name,
                    variable,
                )
                raise ValueError(f"Variable d'environnement {variable} non définie.")

        LOGGER.info("[%s] ----  FIN  ----", methode_name)

    def _charger_nom_scenario(self) -> dict:
        """
        Récupère le nom du scénario à partir de l'environnement.

        Returns:
            str: Nom du scénario
        """

        return {'nom_scenario': os.getenv("NOM_SCENARIO")}

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

        LOGGER.info(
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
        plateforme = (
            os.getenv("PLATEFORME", ConstantesSimulateur.PLATEFORME_PROD)
            .lower()
            .strip()
        )

        if plateforme not in ConstantesSimulateur.PLATEFORMES_VALIDES:
            raise ValueError(
                f"PLATEFORME '{plateforme}' invalide. "
                f"Valeurs autorisées : {', '.join(ConstantesSimulateur.PLATEFORMES_VALIDES)}",
            )

        return {'plateforme': plateforme}

    def _charger_type_scenario(self) -> dict:
        """
        Récupère la variable d'environnement TYPE_SCENARIO

        Returns:
            str: Variable du type de scénario (WEB, EXADATA, TECHNIQUE)
        """
        type_scenario = (
            os.getenv("TYPE_SCENARIO", ConstantesSimulateur.TYPE_SCENARIO_WEB)
            .lower()
            .strip()
        )

        if type_scenario not in ConstantesSimulateur.TYPES_SCENARIO_VALIDES:
            raise ValueError(
                f"TYPE_SCENARIO '{type_scenario}' invalide. "
                f"Valeurs autorisées : {', '.join(ConstantesSimulateur.TYPES_SCENARIO_VALIDES)}",
            )

        return {'type_scenario': type_scenario}

    def _charger_nom_vm_windows(self) -> dict:
        """
        Récupère la variable d'environnement NOM_VM_WINDOWS

        Returns:
            str:
        """

        # TODO : Voir si on créé des constantes pour les nom des VM

        # Si le type de scénario est exadata il faut appeler cette variable
        # et elle est obligatoire sinon on arrête le scénario

        return {'nom_vm_windows': os.getenv("NOM_VM_WINDOWS")}
