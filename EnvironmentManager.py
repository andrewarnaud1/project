
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
- Conversion automatique des types (boolean, chemins, URLs)
- Gestion des erreurs avec messages explicites

Exemple d'utilisation:
---------------------
>>> from src.utils.environment_manager import EnvironmentManager
>>> 
>>> manager = EnvironmentManager()
>>> environnement = manager.charger_variables_environnement()
>>> print(environnement['scenario'])  # Nom du scénario
>>> print(environnement['headless'])  # True/False

Variables d'environnement supportées:
------------------------------------
- SCENARIO (obligatoire) : Nom du scénario à exécuter
- BROWSER : Navigateur à utiliser (firefox, chromium, msedge)
- PLATEFORME : Environnement d'exécution (dev, test, prod)
- HEADLESS : Mode sans interface graphique (true/false)
- LECTURE : Activation de la lecture API (true/false)
- INSCRIPTION : Activation de l'inscription API (true/false)
- PROXY : Configuration du proxy
- SIMU_PATH : Chemin d'installation du simulateur
- SIMU_SCENARIOS : Chemin des scénarios
- SIMU_OUTPUT : Chemin de sortie des rapports
- URL_BASE_API_INJECTEUR : URL de base de l'API
- PATH_UTILISATEURS_ISAC : Chemin des fichiers utilisateurs
- PLAYWRIGHT_BROWSERS_PATH : Chemin des navigateurs Playwright
- NOM_VM_WINDOWS : Nom de la VM Windows pour Guacamole

Auteur: Équipe Simulateur V6
Version: 1.0.0
"""

import os
import logging
import pytest
from typing import Dict, Any
from src.utils.utils import contexte_actuel

LOGGER = logging.getLogger(__name__)


class EnvironmentManager:
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
        pass
    
    def charger_variables_environnement(self) -> Dict[str, Any]:
        """
        Charge et valide toutes les variables d'environnement nécessaires.
        
        Returns:
            Dict[str, Any]: Dictionnaire contenant toutes les variables d'environnement
                           avec leurs valeurs typées et validées
        
        Raises:
            SystemExit: Si une variable obligatoire est manquante
        """
        methode_name = contexte_actuel(self)
        LOGGER.debug("[%s] ---- DEBUT ----", methode_name)
        
        environnement = {}
        
        # Variables obligatoires
        environnement['scenario'] = os.environ.get('SCENARIO')
        if not environnement['scenario']:
            LOGGER.fatal("[%s] ❌ Variable d'environnement SCENARIO non définie.", methode_name)
            pytest.exit(2)
        
        LOGGER.info("Scenario [%s] ---- DEBUT ----", environnement['scenario'])
        
        # Navigateur depuis l'environnement (optionnel)
        if 'BROWSER' in os.environ:
            environnement['navigateur'] = os.getenv('BROWSER')
            LOGGER.info(
                "[%s] Navigateur fixé par l'environnement : %s",
                methode_name, environnement['navigateur']
            )
        
        # Variables avec valeurs par défaut
        environnement['simu_path'] = os.environ.get('SIMU_PATH', '/opt/simulateur_v6')
        environnement['simu_scenarios'] = os.getenv('SIMU_SCENARIOS', '/opt/scenarios_v6')
        environnement['path_utilisateurs_isac'] = os.environ.get(
            'PATH_UTILISATEURS_ISAC', environnement['simu_path']
        )
        environnement['simu_output'] = os.environ.get('SIMU_OUTPUT', '/var/simulateur_v6')
        environnement['url_base_api_injecteur'] = os.environ.get(
            'URL_BASE_API_INJECTEUR', 'http://localhost/'
        )
        environnement['plateforme'] = os.environ.get('PLATEFORME', 'prod')
        environnement['proxy'] = os.getenv('PROXY')
        
        # Variables booléennes
        lecture_env = os.getenv('LECTURE', 'true').lower()
        environnement['lecture'] = lecture_env != 'false'
        
        inscription_env = os.getenv('INSCRIPTION', 'true').lower()
        environnement['inscription'] = (
            environnement['lecture'] and inscription_env != 'false'
        )
        
        headless_env = os.getenv('HEADLESS', 'true').lower()
        environnement['headless'] = headless_env != 'false'
        
        # Valeurs dérivées
        environnement['playwright_browsers_path'] = os.getenv(
            'PLAYWRIGHT_BROWSERS_PATH', environnement['simu_path'] + '/browsers'
        )
        environnement['nom_vm_windows'] = os.getenv('NOM_VM_WINDOWS', '')
        
        LOGGER.debug("[%s] environnement => %s", methode_name, environnement)
        LOGGER.debug("[%s] ----  FIN  ----", methode_name)
        return environnement
