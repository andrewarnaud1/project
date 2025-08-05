“””
constantes.py - Version simplifiée pour les phases d’initialisation

Constantes simples avec incrémentation automatique sans classes complexes.
“””

class ConstantesSimulateur:
“””
Constantes utilisées par le simulateur
“””

```
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

# === PHASES D'INITIALISATION ===

# Phases pré-API (1-4)
PHASE_ENVIRONNEMENT = 1
PHASE_CONFIG_BASE = 2
PHASE_API = 3
PHASE_PLANNING = 4

# Phases post-API (5-6)
PHASE_CONFIG_FINALE = 5
PHASE_REPERTOIRES = 6

# Noms des phases (pour logs)
NOMS_PHASES = {
    1: "CHARGEMENT_ENVIRONNEMENT",
    2: "CONFIGURATION_BASE", 
    3: "LECTURE_API",
    4: "VERIFICATION_PLANNING",
    5: "CONFIGURATION_FINALE",
    6: "CREATION_REPERTOIRES"
}

# Descriptions des phases
DESCRIPTIONS_PHASES = {
    1: "Chargement et validation de l'environnement",
    2: "Chargement de la configuration de base (identifiant)",
    3: "Lecture des données API avec l'identifiant", 
    4: "Vérification du planning d'exécution",
    5: "Finalisation de la configuration avec les données API",
    6: "Création des répertoires de sortie"
}

# Séparation pré/post API
PHASES_PRE_API = [1, 2, 3, 4]
PHASES_POST_API = [5, 6]
TOUTES_PHASES = PHASES_PRE_API + PHASES_POST_API

@classmethod
def get_nom_phase(cls, phase_num: int) -> str:
    """Retourne le nom d'une phase"""
    return cls.NOMS_PHASES.get(phase_num, f"PHASE_INCONNUE_{phase_num}")

@classmethod
def get_description_phase(cls, phase_num: int) -> str:
    """Retourne la description d'une phase"""
    return cls.DESCRIPTIONS_PHASES.get(phase_num, f"Description non disponible pour la phase {phase_num}")

@classmethod
def est_phase_pre_api(cls, phase_num: int) -> bool:
    """Vérifie si une phase est pré-API"""
    return phase_num in cls.PHASES_PRE_API

@classmethod
def est_phase_post_api(cls, phase_num: int) -> bool:
    """Vérifie si une phase est post-API"""
    return phase_num in cls.PHASES_POST_API
```

# === EXEMPLE D’UTILISATION SIMPLE ===

if **name** == “**main**”:
print(”=== PHASES D’INITIALISATION ===”)

```
for phase in ConstantesSimulateur.TOUTES_PHASES:
    nom = ConstantesSimulateur.get_nom_phase(phase)
    desc = ConstantesSimulateur.get_description_phase(phase)
    type_phase = "PRÉ-API" if ConstantesSimulateur.est_phase_pre_api(phase) else "POST-API"
    
    print(f"Phase {phase}: {nom}")
    print(f"  Description: {desc}")
    print(f"  Type: {type_phase}")
    print()
```