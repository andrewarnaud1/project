"""
Module des constantes du simulateur.
"""


class ConstantesSimulateur:
    """
    Constantes utilisées par le simulateur
    """

    # Valeurs booléennes
    VALEURS_BOOLEAN_TRUE = ["true", "1", "yes", "on"]
    VALEURS_BOOLEAN_FALSE = ["false", "0", "no", "off"]
    VALEURS_BOOLEAN_VALIDES = VALEURS_BOOLEAN_TRUE + VALEURS_BOOLEAN_FALSE

    # Types de scénarios
    TYPE_SCENARIO_WEB = "web"
    TYPE_SCENARIO_EXADATA = "exadata"
    TYPE_SCENARIO_TECHNIQUE = "technique"
    TYPES_SCENARIO_VALIDES = [
        TYPE_SCENARIO_WEB,
        TYPE_SCENARIO_EXADATA,
        TYPE_SCENARIO_TECHNIQUE,
    ]

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

    # Valeurs par défaut des chemins
    DEFAUT_SIMU_PATH = "/opt/simulateur_v6"
    DEFAUT_SCENARIOS_PATH = "/opt/scenarios_v6"
    DEFAUT_OUTPUT_PATH = "/var/simulateur_v6"
    DEFAUT_URL_API = "http://localhost/"

    # Sous-répertoires relatifs
    UTILISATEURS_ISAC = "config/utilisateurs"
    NAVIGATEURS_PW_PATH = "browsers"
