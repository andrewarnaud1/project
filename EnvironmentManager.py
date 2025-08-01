“””
Module EnvironmentManager - Gestionnaire des variables d’environnement

Ce module centralise la lecture et la validation des variables d’environnement
nécessaires à l’exécution des scénarios de test automatisés.

## Classes:

- EnvironmentError : Exception personnalisée pour les erreurs d’environnement
- EnvironmentConstants : Constantes pour la validation des variables
- EnvironmentManager : Classe principale pour la gestion des variables d’environnement

## Fonctionnalités:

- Lecture des variables d’environnement avec valeurs par défaut
- Validation des variables obligatoires avec types d’erreur spécifiques
- Gestion des erreurs avec exceptions typées (CONFIG/INFRASTRUCTURE)
- Support des différents types de scénarios (WEB, EXADATA, TECHNIQUE)

## Architecture des erreurs:

- EnvironmentManager lève des EnvironmentError avec error_type
- execution.py intercepte ces exceptions et détermine le statut final
- Aucun appel direct à pytest.exit() dans ce module

## Types d’erreurs:

- CONFIG : Variables manquantes, valeurs invalides, configuration incohérente
- INFRASTRUCTURE : Chemins inaccessibles, permissions, problèmes système

## Exemple d’utilisation:

> > > 
> > > 
> > > from src.utils.environment_manager import EnvironmentManager, EnvironmentError
> > > 
> > > try:
> > > manager = EnvironmentManager()
> > > environnement = manager.charger_variables_environnement()
> > > except EnvironmentError as e:
> > > # execution.py gère cette exception
> > > if e.error_type == “CONFIG”:
> > > # Statut 2 - Erreur applicative/configuration
> > > elif e.error_type == “INFRASTRUCTURE”:
> > > # Statut 3 - Erreur infrastructure/système

## Variables d’environnement supportées:

OBLIGATOIRES:

- SCENARIO : Nom du scénario à exécuter
- TYPE_SCENARIO : Type de scénario (WEB, EXADATA, TECHNIQUE)

OPTIONNELLES avec valeurs par défaut:

- NAVIGATEUR : Navigateur (firefox, chromium, msedge) [défaut: firefox]
- PLATEFORME : Environnement (dev, test, prod) [défaut: prod]
- HEADLESS : Mode sans interface (true/false) [défaut: true]
- LECTURE : Activation lecture API (true/false) [défaut: true]
- INSCRIPTION : Activation inscription API (true/false) [défaut: true]
- PROXY : Configuration proxy [défaut: ‘’]

CHEMINS avec valeurs par défaut:

- SIMU_PATH : Installation simulateur [défaut: /opt/simulateur_v6]
- SCENARIOS_PATH : Répertoire scénarios [défaut: /opt/scenarios_v6]
- OUTPUT_PATH : Répertoire rapports [défaut: /var/simulateur_v6]
- URL_BASE_API_INJECTEUR : URL API [défaut: http://localhost/]
- UTILISATEURS_ISAC_PATH : Fichiers utilisateurs [défaut: auto-généré]
- PLAYWRIGHT_NAVIGATEURS_PATH : Navigateurs [défaut: auto-généré]

CONDITIONNELLES:

- NOM_VM_WINDOWS : Obligatoire si TYPE_SCENARIO=EXADATA
  “””

import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from src.utils.utils import contexte_actuel

LOGGER = logging.getLogger(**name**)

class EnvironmentError(Exception):
“””
Exception personnalisée pour les erreurs de variables d’environnement.

```
Cette exception permet de typer les erreurs pour que execution.py
puisse déterminer le bon statut de sortie.

Attributes:
    message (str): Message d'erreur détaillé
    error_type (str): Type d'erreur ("CONFIG" ou "INFRASTRUCTURE")
    variable_name (str): Nom de la variable concernée (optionnel)
"""

def __init__(self, message: str, error_type: str, variable_name: Optional[str] = None):
    """
    Initialise une erreur d'environnement.
    
    Args:
        message: Message d'erreur descriptif
        error_type: "CONFIG" pour erreur de configuration, "INFRASTRUCTURE" pour erreur système
        variable_name: Nom de la variable en erreur (optionnel)
    """
    self.message = message
    self.error_type = error_type  # "CONFIG" ou "INFRASTRUCTURE"
    self.variable_name = variable_name
    super().__init__(self.message)

def __str__(self):
    if self.variable_name:
        return f"[{self.variable_name}] {self.message}"
    return self.message
```

class EnvironmentConstants:
“””
Constantes pour la validation des variables d’environnement.

```
Cette classe centralise toutes les valeurs autorisées et les valeurs
par défaut pour maintenir la cohérence et faciliter la maintenance.
"""

# Types de scénarios
TYPE_SCENARIO_WEB = "WEB"
TYPE_SCENARIO_EXADATA = "EXADATA"
TYPE_SCENARIO_TECHNIQUE = "TECHNIQUE"
TYPES_SCENARIO_VALIDES = [TYPE_SCENARIO_WEB, TYPE_SCENARIO_EXADATA, TYPE_SCENARIO_TECHNIQUE]

# Navigateurs supportés
NAVIGATEUR_FIREFOX = "firefox"
NAVIGATEUR_CHROMIUM = "chromium"
NAVIGATEUR_MSEDGE = "msedge"
NAVIGATEURS_VALIDES = [NAVIGATEUR_FIREFOX, NAVIGATEUR_CHROMIUM, NAVIGATEUR_MSEDGE]

# Plateformes supportées
PLATEFORME_DEV = "dev"
PLATEFORME_TEST = "test"
PLATEFORME_PROD = "prod"
PLATEFORMES_VALIDES = [PLATEFORME_DEV, PLATEFORME_TEST, PLATEFORME_PROD]

# Valeurs booléennes autorisées
VALEURS_BOOLEAN_TRUE = ["true", "1", "yes", "on"]
VALEURS_BOOLEAN_FALSE = ["false", "0", "no", "off"]
VALEURS_BOOLEAN_VALIDES = VALEURS_BOOLEAN_TRUE + VALEURS_BOOLEAN_FALSE

# Valeurs par défaut des chemins système
CHEMIN_DEFAUT_SIMU_PATH = "/opt/simulateur_v6"
CHEMIN_DEFAUT_SCENARIOS_PATH = "/opt/scenarios_v6"
CHEMIN_DEFAUT_OUTPUT_PATH = "/var/simulateur_v6"
CHEMIN_DEFAUT_URL_API = "http://localhost/"

# Sous-répertoires relatifs
SOUS_REP_UTILISATEURS_ISAC = "config/utilisateurs"
SOUS_REP_BROWSERS = "browsers"

# Types d'erreurs pour execution.py
ERROR_TYPE_CONFIG = "CONFIG"
ERROR_TYPE_INFRASTRUCTURE = "INFRASTRUCTURE"
```

class EnvironmentManager:
“””
Gestionnaire des variables d’environnement pour l’exécution des scénarios.

```
Cette classe centralise la lecture, la validation et la conversion
des variables d'environnement nécessaires au bon fonctionnement
du simulateur de tests automatisés.

La classe lève des EnvironmentError typées que execution.py intercepte
pour déterminer le statut de sortie approprié :
- CONFIG : Erreurs de configuration/applicatives → Statut 2
- INFRASTRUCTURE : Erreurs d'infrastructure/système → Statut 3
"""

def __init__(self):
    """
    Initialise le gestionnaire des variables d'environnement.
    """
    self.methode_name = contexte_actuel(self)
    LOGGER.debug("[%s] ---- DEBUT INITIALISATION ----", self.methode_name)
    LOGGER.debug("[%s] ---- FIN INITIALISATION ----", self.methode_name)

def charger_variables_environnement(self) -> Dict[str, Any]:
    """
    Charge et valide toutes les variables d'environnement nécessaires.

    Returns:
        Dict[str, Any]: Dictionnaire contenant toutes les variables d'environnement
                       avec leurs valeurs validées
    
    Raises:
        EnvironmentError: 
            - error_type="CONFIG" : Variables obligatoires manquantes, valeurs invalides
            - error_type="INFRASTRUCTURE" : Problèmes d'accès système, chemins inaccessibles
    """
    methode_name = contexte_actuel(self)
    LOGGER.debug("[%s] ---- DEBUT CHARGEMENT ----", methode_name)
    
    try:
        environnement = {}
        
        # 1. Chargement des variables de base (obligatoires)
        environnement.update(self._charger_variables_base())
        
        # 2. Chargement des chemins système
        environnement.update(self._charger_chemins())
        
        # 3. Chargement des paramètres API
        environnement.update(self._charger_variables_api())
        
        # 4. Chargement des paramètres navigateur
        environnement.update(self._charger_parametres_navigateur())
        
        # 5. Chargement des variables conditionnelles selon le type de scénario
        environnement.update(self._charger_variables_conditionnelles(environnement))
        
        # 6. Validation finale des chemins critiques
        self._valider_chemins_critiques(environnement)
        
        LOGGER.info("[%s] ✅ Variables d'environnement chargées avec succès", methode_name)
        LOGGER.debug("[%s] Variables chargées : %s", methode_name, list(environnement.keys()))
        
        return environnement
        
    except EnvironmentError:
        # Re-propagation des erreurs typées sans modification
        raise
    except Exception as e:
        # Conversion des erreurs système inattendues
        LOGGER.error("[%s] ❌ Erreur inattendue lors du chargement : %s", methode_name, e)
        raise EnvironmentError(
            f"Erreur système inattendue lors du chargement des variables : {e}",
            error_type=EnvironmentConstants.ERROR_TYPE_INFRASTRUCTURE
        ) from e
    finally:
        LOGGER.debug("[%s] ---- FIN CHARGEMENT ----", methode_name)

def _charger_variables_base(self) -> Dict[str, Any]:
    """
    Charge les variables d'environnement de base obligatoires.
    
    Returns:
        Dict[str, Any]: Variables de base validées
        
    Raises:
        EnvironmentError: error_type="CONFIG" si variables manquantes ou invalides
    """
    variables = {}
    
    # SCENARIO (obligatoire)
    scenario = os.getenv("SCENARIO")
    if not scenario or not scenario.strip():
        raise EnvironmentError(
            "Variable d'environnement SCENARIO obligatoire non définie ou vide",
            error_type=EnvironmentConstants.ERROR_TYPE_CONFIG,
            variable_name="SCENARIO"
        )
    variables["scenario"] = scenario.strip()
    
    # TYPE_SCENARIO (obligatoire)
    type_scenario = os.getenv("TYPE_SCENARIO")
    if not type_scenario or not type_scenario.strip():
        raise EnvironmentError(
            "Variable d'environnement TYPE_SCENARIO obligatoire non définie ou vide",
            error_type=EnvironmentConstants.ERROR_TYPE_CONFIG,
            variable_name="TYPE_SCENARIO"
        )
    
    type_scenario = type_scenario.upper().strip()
    if type_scenario not in EnvironmentConstants.TYPES_SCENARIO_VALIDES:
        raise EnvironmentError(
            f"TYPE_SCENARIO '{type_scenario}' invalide. "
            f"Valeurs autorisées : {', '.join(EnvironmentConstants.TYPES_SCENARIO_VALIDES)}",
            error_type=EnvironmentConstants.ERROR_TYPE_CONFIG,
            variable_name="TYPE_SCENARIO"
        )
    variables["type_scenario"] = type_scenario
    
    # PLATEFORME (optionnelle avec validation)
    plateforme = os.getenv("PLATEFORME", EnvironmentConstants.PLATEFORME_PROD).lower().strip()
    if plateforme not in EnvironmentConstants.PLATEFORMES_VALIDES:
        raise EnvironmentError(
            f"PLATEFORME '{plateforme}' invalide. "
            f"Valeurs autorisées : {', '.join(EnvironmentConstants.PLATEFORMES_VALIDES)}",
            error_type=EnvironmentConstants.ERROR_TYPE_CONFIG,
            variable_name="PLATEFORME"
        )
    variables["plateforme"] = plateforme
    
    LOGGER.debug("[_charger_variables_base] Variables de base chargées : %s", 
                list(variables.keys()))
    return variables

def _charger_chemins(self) -> Dict[str, Any]:
    """
    Charge et valide les chemins système.
    
    Returns:
        Dict[str, Any]: Chemins système avec valeurs par défaut
        
    Raises:
        EnvironmentError: error_type="CONFIG" si chemins mal formés
    """
    chemins = {}
    
    # Chemins principaux avec valeurs par défaut
    chemins["simu_path"] = os.getenv("SIMU_PATH", EnvironmentConstants.CHEMIN_DEFAUT_SIMU_PATH)
    chemins["scenarios_path"] = os.getenv("SCENARIOS_PATH", EnvironmentConstants.CHEMIN_DEFAUT_SCENARIOS_PATH)
    chemins["output_path"] = os.getenv("OUTPUT_PATH", EnvironmentConstants.CHEMIN_DEFAUT_OUTPUT_PATH)
    
    # URL API
    chemins["url_base_api_injecteur"] = os.getenv("URL_BASE_API_INJECTEUR", EnvironmentConstants.CHEMIN_DEFAUT_URL_API)
    
    # Chemins calculés à partir des chemins principaux
    chemins["utilisateurs_isac_path"] = os.getenv(
        "UTILISATEURS_ISAC_PATH", 
        f"{chemins['scenarios_path']}/{EnvironmentConstants.SOUS_REP_UTILISATEURS_ISAC}"
    )
    
    chemins["playwright_browsers_path"] = os.getenv(
        "PLAYWRIGHT_NAVIGATEURS_PATH", 
        f"{chemins['simu_path']}/{EnvironmentConstants.SOUS_REP_BROWSERS}"
    )
    
    # Validation des formats des chemins
    for nom_chemin, chemin in chemins.items():
        if not chemin or not isinstance(chemin, str) or not chemin.strip():
            raise EnvironmentError(
                f"Chemin {nom_chemin} vide ou invalide : '{chemin}'",
                error_type=EnvironmentConstants.ERROR_TYPE_CONFIG,
                variable_name=nom_chemin.upper()
            )
        
        # Normalisation du chemin (suppression des espaces)
        chemins[nom_chemin] = chemin.strip()
    
    LOGGER.debug("[_charger_chemins] Chemins chargés : %s", list(chemins.keys()))
    return chemins

def _charger_variables_api(self) -> Dict[str, Any]:
    """
    Charge les variables de configuration de l'API.
    
    Returns:
        Dict[str, Any]: Variables API
    """
    variables_api = {}
    
    # LECTURE (défaut: true)
    lecture_env = os.getenv("LECTURE", "true").lower().strip()
    variables_api["lecture"] = self._convertir_boolean(lecture_env, "LECTURE")
    
    # INSCRIPTION (défaut: true, mais dépend de LECTURE)
    inscription_env = os.getenv("INSCRIPTION", "true").lower().strip()
    inscription_bool = self._convertir_boolean(inscription_env, "INSCRIPTION")
    # Si lecture est False, inscription est forcément False
    variables_api["inscription"] = variables_api["lecture"] and inscription_bool
    
    LOGGER.debug("[_charger_variables_api] Variables API chargées : %s", list(variables_api.keys()))
    return variables_api

def _charger_parametres_navigateur(self) -> Dict[str, Any]:
    """
    Charge les paramètres de configuration du navigateur.
    
    Returns:
        Dict[str, Any]: Paramètres navigateur
        
    Raises:
        EnvironmentError: error_type="CONFIG" si navigateur invalide
    """
    parametres = {}
    
    # NAVIGATEUR (défaut: firefox)
    navigateur = os.getenv("NAVIGATEUR", EnvironmentConstants.NAVIGATEUR_FIREFOX).lower().strip()
    if navigateur not in EnvironmentConstants.NAVIGATEURS_VALIDES:
        raise EnvironmentError(
            f"NAVIGATEUR '{navigateur}' invalide. "
            f"Valeurs autorisées : {', '.join(EnvironmentConstants.NAVIGATEURS_VALIDES)}",
            error_type=EnvironmentConstants.ERROR_TYPE_CONFIG,
            variable_name="NAVIGATEUR"
        )
    parametres["navigateur"] = navigateur
    
    # HEADLESS (défaut: true)
    headless_env = os.getenv("HEADLESS", "true").lower().strip()
    parametres["headless"] = self._convertir_boolean(headless_env, "HEADLESS")
    
    # PROXY (optionnel)
    parametres["proxy"] = os.getenv("PROXY", "").strip()
    
    LOGGER.debug("[_charger_parametres_navigateur] Paramètres navigateur chargés : %s", 
                list(parametres.keys()))
    return parametres

def _charger_variables_conditionnelles(self, environnement: Dict[str, Any]) -> Dict[str, Any]:
    """
    Charge les variables conditionnelles selon le type de scénario.
    
    Args:
        environnement: Variables déjà chargées (pour accéder au type_scenario)
        
    Returns:
        Dict[str, Any]: Variables conditionnelles
        
    Raises:
        EnvironmentError: error_type="CONFIG" si variables conditionnelles manquantes
    """
    variables_conditionnelles = {}
    
    type_scenario = environnement.get("type_scenario")
    
    # Pour les scénarios EXADATA, NOM_VM_WINDOWS est obligatoire
    if type_scenario == EnvironmentConstants.TYPE_SCENARIO_EXADATA:
        nom_vm_windows = os.getenv("NOM_VM_WINDOWS")
        if not nom_vm_windows or not nom_vm_windows.strip():
            raise EnvironmentError(
                "Variable NOM_VM_WINDOWS obligatoire pour les scénarios de type EXADATA",
                error_type=EnvironmentConstants.ERROR_TYPE_CONFIG,
                variable_name="NOM_VM_WINDOWS"
            )
        variables_conditionnelles["nom_vm_windows"] = nom_vm_windows.strip()
    
    LOGGER.debug("[_charger_variables_conditionnelles] Variables conditionnelles pour %s : %s", 
                type_scenario, list(variables_conditionnelles.keys()))
    return variables_conditionnelles

def _valider_chemins_critiques(self, environnement: Dict[str, Any]) -> None:
    """
    Valide l'accessibilité des chemins critiques pour le fonctionnement.
    
    Args:
        environnement: Variables d'environnement chargées
        
    Raises:
        EnvironmentError: error_type="INFRASTRUCTURE" si chemins inaccessibles
    """
    # Chemins critiques à vérifier
    chemins_critiques = ["scenarios_path", "simu_path"]
    
    for nom_chemin in chemins_critiques:
        chemin = environnement.get(nom_chemin)
        if chemin:
            path_obj = Path(chemin)
            try:
                # Vérification d'existence et d'accès en lecture
                if not path_obj.exists():
                    raise EnvironmentError(
                        f"Chemin critique {nom_chemin} inexistant : {chemin}",
                        error_type=EnvironmentConstants.ERROR_TYPE_INFRASTRUCTURE,
                        variable_name=nom_chemin.upper()
                    )
                
                if not os.access(chemin, os.R_OK):
                    raise EnvironmentError(
                        f"Chemin critique {nom_chemin} inaccessible en lecture : {chemin}",
                        error_type=EnvironmentConstants.ERROR_TYPE_INFRASTRUCTURE,
                        variable_name=nom_chemin.upper()
                    )
                    
            except OSError as e:
                raise EnvironmentError(
                    f"Erreur système lors de la vérification du chemin {nom_chemin} ({chemin}) : {e}",
                    error_type=EnvironmentConstants.ERROR_TYPE_INFRASTRUCTURE,
                    variable_name=nom_chemin.upper()
                ) from e
    
    LOGGER.debug("[_valider_chemins_critiques] Validation des chemins critiques réussie")

def _convertir_boolean(self, valeur: str, nom_variable: str) -> bool:
    """
    Convertit une chaîne en booléen selon les constantes définies.
    
    Args:
        valeur: Valeur à convertir
        nom_variable: Nom de la variable (pour les erreurs)
        
    Returns:
        bool: Valeur booléenne
        
    Raises:
        EnvironmentError: error_type="CONFIG" si valeur invalide
    """
    valeur_lower = valeur.lower().strip()
    
    if valeur_lower in EnvironmentConstants.VALEURS_BOOLEAN_TRUE:
        return True
    elif valeur_lower in EnvironmentConstants.VALEURS_BOOLEAN_FALSE:
        return False
    else:
        raise EnvironmentError(
            f"Valeur booléenne invalide pour {nom_variable} : '{valeur}'. "
            f"Valeurs autorisées : {', '.join(EnvironmentConstants.VALEURS_BOOLEAN_VALIDES)}",
            error_type=EnvironmentConstants.ERROR_TYPE_CONFIG,
            variable_name=nom_variable
        )
```