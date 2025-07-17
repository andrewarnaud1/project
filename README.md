"""
=== 1. config/patterns_erreurs.yaml ===
Fichier unique de configuration des erreurs
"""

# Configuration des patterns d'erreur HTTP
detection_erreurs:
  # Patterns pour trouver les codes d'erreur HTTP (400, 500, etc.)
  codes_http:
    - 'error\s*code\s*:\s*([45]\d{2})'         # Error code: 500
    - 'code\s*erreur\s*:\s*([45]\d{2})'        # Code erreur: 500
    - 'responsestatus[^"]*:([45]\d{2})'        # Firefox responsestatus:500
    - 'status\s*:\s*([45]\d{2})'               # Status: 500
    - 'http/1\.[01]\s+([45]\d{2})'             # HTTP/1.1 500
    - '<h1[^>]*>([45]\d{2})'                   # <h1>500</h1>

  # Messages d'erreur sans code spécifique
  messages_erreur:
    # Erreurs serveur (5xx)
    "5xx":
      - 'internal\s*server\s*error'
      - 'erreur\s*interne\s*du\s*serveur'
      - 'service\s*unavailable'
      - 'service\s*indisponible'
      - 'bad\s*gateway'
      - 'gateway\s*timeout'
      - 'server\s*error'
      - 'erreur\s*serveur'
      - 'maintenance\s*en\s*cours'
      - 'application\s*temporairement\s*indisponible'
    
    # Erreurs client (4xx)
    "4xx":
      - 'not\s*found'
      - 'page\s*introuvable'
      - 'forbidden'
      - 'accès\s*interdit'
      - 'unauthorized'
      - 'non\s*autorisé'
      - 'session\s*expirée'
    
    # Erreurs génériques
    "autre":
      - 'looks\s*like.*problem.*site'
      - 'problème.*site'
      - 'une\s*erreur.*produite'

  # Sélecteurs CSS pour chercher dans les éléments
  selecteurs:
    # IDs d'erreur
    - '#errorShortDesc'
    - '#response-status-label'
    - '#error'
    - '#erreur'
    - '#error-message'
    - '#app-error-container'
    
    # Classes d'erreur
    - '.error'
    - '.erreur'
    - '.alert-error'
    - '.alert-danger'
    - '.message-error'
    - '.notification-error'
    
    # Éléments HTML
    - 'h1'
    - '.title-text'
    - '[data-l10n-id*="error"]'
    - '[data-error-type]'

# Descriptions des codes d'erreur
descriptions_codes:
  400: "Requête incorrecte"
  401: "Non autorisé"
  403: "Accès interdit"
  404: "Page non trouvée"
  405: "Méthode non autorisée"
  408: "Timeout de la requête"
  429: "Trop de requêtes"
  500: "Erreur interne du serveur"
  501: "Non implémenté"
  502: "Mauvaise passerelle"
  503: "Service indisponible"
  504: "Timeout de la passerelle"
  505: "Version HTTP non supportée"

# Descriptions des types d'erreur
descriptions_types:
  "4xx": "Erreur client"
  "5xx": "Erreur serveur"
  "3xx": "Redirection"
  "autre": "Erreur HTTP"


"""
=== 2. src/utils/verificateur_timeout.py ===
Vérificateur de timeout simplifié
"""

import logging
import re
from typing import List, Optional, Dict
from playwright.sync_api import Page
from src.utils.yaml_loader import load_yaml_file

LOGGER = logging.getLogger(__name__)

class VerificateurTimeout:
    """Vérificateur de timeout avec configuration externe simple"""
    
    def __init__(self, config_execution: Dict):
        self.config_execution = config_execution
        self.patterns = self._charger_patterns()
    
    def _charger_patterns(self) -> Dict:
        """Charge les patterns d'erreur depuis le fichier YAML"""
        try:
            simu_scenarios = self.config_execution.get('simu_scenarios', '/opt/scenarios_v6')
            chemin_config = f"{simu_scenarios}/config/patterns_erreurs.yaml"
            
            patterns = load_yaml_file(chemin_config)
            LOGGER.debug("[VerificateurTimeout] Patterns d'erreur chargés")
            return patterns
        except Exception as e:
            LOGGER.warning(f"[VerificateurTimeout] Erreur chargement patterns: {e}")
            return self._patterns_par_defaut()
    
    def _patterns_par_defaut(self) -> Dict:
        """Patterns par défaut si le fichier n'est pas accessible"""
        return {
            'detection_erreurs': {
                'codes_http': [
                    'error\s*code\s*:\s*([45]\\d{2})',
                    'responsestatus[^"]*:([45]\\d{2})'
                ],
                'messages_erreur': {
                    '5xx': ['internal\\s*server\\s*error', 'service\\s*unavailable'],
                    '4xx': ['not\\s*found', 'forbidden'],
                    'autre': ['problem.*site']
                },
                'selecteurs': ['#errorShortDesc', '.error', 'h1']
            },
            'descriptions_codes': {500: 'Erreur serveur', 404: 'Page non trouvée'},
            'descriptions_types': {'4xx': 'Erreur client', '5xx': 'Erreur serveur', 'autre': 'Erreur HTTP'}
        }
    
    def verifier_cause_timeout(self, page: Page) -> Optional[str]:
        """
        Vérifie si un timeout est causé par une erreur HTTP
        
        Returns:
            str: Message d'erreur HTTP ou None si pas d'erreur
        """
        try:
            # Chercher dans la page principale
            erreurs = self._chercher_erreurs_dans_page(page)
            
            # Chercher dans toutes les frames
            for frame in page.frames:
                if frame != page.main_frame:
                    try:
                        erreurs_frame = self._chercher_erreurs_dans_page(frame)
                        erreurs.extend(erreurs_frame)
                    except Exception as e:
                        LOGGER.debug(f"[VerificateurTimeout] Erreur frame {frame.url}: {e}")
                        continue
            
            # Retourner la première erreur trouvée
            if erreurs:
                return erreurs[0]
            
            return None
            
        except Exception as e:
            LOGGER.debug(f"[VerificateurTimeout] Erreur vérification: {e}")
            return None
    
    def _chercher_erreurs_dans_page(self, page_ou_frame) -> List[str]:
        """Cherche les erreurs dans une page ou frame"""
        erreurs = []
        
        try:
            # Récupérer le contenu HTML
            contenu_html = page_ou_frame.content()
            
            # Chercher les codes d'erreur spécifiques
            erreurs_codes = self._chercher_codes_erreur(contenu_html)
            erreurs.extend(erreurs_codes)
            
            # Si pas de code trouvé, chercher les messages génériques
            if not erreurs_codes:
                erreurs_messages = self._chercher_messages_erreur(contenu_html)
                erreurs.extend(erreurs_messages)
            
            # Chercher dans les éléments visibles
            erreurs_elements = self._chercher_dans_elements(page_ou_frame)
            erreurs.extend(erreurs_elements)
            
        except Exception as e:
            LOGGER.debug(f"[VerificateurTimeout] Erreur recherche: {e}")
        
        return erreurs[:2]  # Limiter à 2 erreurs
    
    def _chercher_codes_erreur(self, contenu_html: str) -> List[str]:
        """Cherche les codes d'erreur HTTP dans le HTML"""
        erreurs = []
        html_minuscule = contenu_html.lower()
        
        patterns_codes = self.patterns.get('detection_erreurs', {}).get('codes_http', [])
        
        for pattern in patterns_codes:
            matches = re.finditer(pattern, html_minuscule, re.IGNORECASE)
            for match in matches:
                if match.groups():
                    code_erreur = int(match.group(1))
                    message_formate = self._formater_message_erreur(code_erreur)
                    erreurs.append(message_formate)
                    
                    # Limiter à 2 codes
                    if len(erreurs) >= 2:
                        return erreurs
        
        return erreurs
    
    def _chercher_messages_erreur(self, contenu_html: str) -> List[str]:
        """Cherche les messages d'erreur génériques"""
        erreurs = []
        html_minuscule = contenu_html.lower()
        
        messages_erreur = self.patterns.get('detection_erreurs', {}).get('messages_erreur', {})
        
        for type_erreur, patterns in messages_erreur.items():
            for pattern in patterns:
                if re.search(pattern, html_minuscule, re.IGNORECASE):
                    description_type = self._get_description_type(type_erreur)
                    erreurs.append(f"{description_type} ({type_erreur}) détectée")
                    return erreurs  # Une seule erreur générique
        
        return erreurs
    
    def _chercher_dans_elements(self, page_ou_frame) -> List[str]:
        """Cherche dans les éléments visibles"""
        erreurs = []
        
        selecteurs = self.patterns.get('detection_erreurs', {}).get('selecteurs', [])
        
        for selecteur in selecteurs:
            try:
                elements = page_ou_frame.locator(selecteur).all()
                for element in elements:
                    try:
                        texte = element.inner_text(timeout=500).strip()
                        if texte:
                            # Chercher un code d'erreur dans le texte
                            codes_trouves = re.findall(r'([45]\d{2})', texte)
                            if codes_trouves:
                                code_erreur = int(codes_trouves[0])
                                message_formate = self._formater_message_erreur(code_erreur)
                                erreurs.append(message_formate)
                                return erreurs  # Une seule erreur par élément
                    except:
                        continue
            except:
                continue
        
        return erreurs
    
    def _formater_message_erreur(self, code_erreur: int) -> str:
        """Formate un message d'erreur avec le code HTTP"""
        type_erreur = self._get_type_erreur(code_erreur)
        description_type = self._get_description_type(type_erreur)
        description_code = self._get_description_code(code_erreur)
        
        return f"{description_type} ({type_erreur}) - {code_erreur} {description_code}"
    
    def _get_type_erreur(self, code_erreur: int) -> str:
        """Détermine le type d'erreur (4xx, 5xx, etc.)"""
        if 400 <= code_erreur <= 499:
            return "4xx"
        elif 500 <= code_erreur <= 599:
            return "5xx"
        elif 300 <= code_erreur <= 399:
            return "3xx"
        else:
            return "autre"
    
    def _get_description_type(self, type_erreur: str) -> str:
        """Récupère la description d'un type d'erreur"""
        descriptions = self.patterns.get('descriptions_types', {})
        return descriptions.get(type_erreur, "Erreur inconnue")
    
    def _get_description_code(self, code_erreur: int) -> str:
        """Récupère la description d'un code d'erreur"""
        descriptions = self.patterns.get('descriptions_codes', {})
        return descriptions.get(code_erreur, f"Code {code_erreur}")


"""
=== 3. src/gestion_exception.py ===
Gestionnaire d'exception simplifié
"""

import re
import logging
import pytest
from playwright.sync_api import Page

from src.utils.utils import contexte_actuel
from src.utils.screenshot_manager import take_screenshot
from src.utils.verificateur_timeout import VerificateurTimeout

LOGGER = logging.getLogger(__name__)

def gestion_exception(execution, etape, page: Page, exception: Exception):
    """Gestion des exceptions avec vérification timeout"""
    methode_name = contexte_actuel()
    LOGGER.debug('[%s] ---- DEBUT ----', methode_name)
    
    # URL pour le rapport
    if len(execution.etapes) == 0:
        url = execution.config.get('url_initiale')
    else:
        url = page.url
    
    # Construire le commentaire d'erreur
    commentaire = construire_commentaire_erreur(
        etape.etape['nom'], 
        execution, 
        url, 
        exception, 
        page
    )
    
    LOGGER.error(f"❌ {commentaire}")
    LOGGER.error(f"❌ Exception: {exception}")
    
    etape.finalise(execution.compteur_etape, 2, url, commentaire)
    
    # Screenshot et sortie
    take_screenshot(execution, etape, page, erreur=True)
    LOGGER.info('[%s] Appel de pytest.exit(2)', methode_name)
    pytest.exit(2)


def construire_commentaire_erreur(nom_etape: str, execution, url: str, 
                                exception: Exception, page: Page) -> str:
    """Construit le commentaire d'erreur en vérifiant la cause"""
    
    base_commentaire = f"KO - Etape {execution.compteur_etape} {nom_etape}"
    message_exception = str(exception)
    
    # Vérifier si c'est un timeout
    if est_timeout(message_exception):
        # Créer le vérificateur et analyser la cause
        verificateur = VerificateurTimeout(execution.config)
        cause_timeout = verificateur.verifier_cause_timeout(page)
        
        if cause_timeout:
            # Timeout causé par une erreur HTTP
            return f"{base_commentaire} : 🌐 Timeout dû à une erreur HTTP - {cause_timeout}"
        else:
            # Timeout normal
            message_nettoye = nettoyer_message_timeout(message_exception)
            return f"{base_commentaire} : ⏱️ {message_nettoye}"
    else:
        # Autre type d'erreur
        message_nettoye = nettoyer_message_erreur(message_exception, execution, url)
        return f"{base_commentaire} : {message_nettoye}"


def est_timeout(message_exception: str) -> bool:
    """Vérifie si l'exception est un timeout"""
    mots_cles_timeout = [
        'timeout', 'timed out', 'exceeded', 'délai', 'dépassé',
        'wait_for', 'waiting for', 'attente'
    ]
    
    message_minuscule = message_exception.lower()
    return any(mot_cle in message_minuscule for mot_cle in mots_cles_timeout)


def nettoyer_message_timeout(message_exception: str) -> str:
    """Nettoie et traduit les messages de timeout"""
    message = nettoyer_message_base(message_exception)
    
    # Traductions spécifiques aux timeouts
    message = re.sub(r'Locator\.wait_for:', 'Attente élément :', message)
    message = re.sub(r'exceeded', 'dépassé', message)
    message = re.sub(r'to be visible', 'visible', message)
    message = re.sub(r'Call log:.*', '', message)
    message = re.sub(r'\s+', ' ', message).strip()
    
    return message


def nettoyer_message_erreur(message: str, execution, url: str) -> str:
    """Nettoie les messages d'erreur (fonction existante simplifiée)"""
    if 'Page.goto' in message:
        return nettoyer_erreur_navigation(message, execution, url)
    elif 'Locator.wait_for' in message:
        return nettoyer_erreur_attente(message)
    elif 'Locator expected to be visible' in message:
        return nettoyer_erreur_visibilite(message)
    else:
        return nettoyer_message_base(message)


def nettoyer_erreur_navigation(message: str, execution, url: str) -> str:
    """Nettoie les erreurs de navigation"""
    message = re.sub(r"^Page\.goto:", f"Ouverture {url} : ", message)
    message = re.sub(r"Call log:.*$", "", message, flags=re.DOTALL)
    
    # Traduction des codes d'erreur Firefox
    traductions = {
        "NS_ERROR_CONNECTION_REFUSED": "Connexion au serveur refusée",
        "NS_ERROR_NET_TIMEOUT": "Timeout de connexion",
        "NS_ERROR_UNKNOWN_HOST": "Nom d'hôte introuvable",
        "SSL_ERROR_UNKNOWN": "Erreur de connexion sécurisée"
    }
    
    for code, traduction in traductions.items():
        message = re.sub(rf"\b{code}\b", traduction, message)
    
    return message.strip()


def nettoyer_erreur_attente(message: str) -> str:
    """Nettoie les erreurs d'attente d'élément"""
    message = re.sub(r"^Locator.wait_for:", "Attente élément :", message)
    message = re.sub(r"exceeded", "dépassé", message)
    message = re.sub(r"to be visible", "visible", message)
    message = re.sub(r"Call log:.*", "", message)
    return message.strip()


def nettoyer_erreur_visibilite(message: str) -> str:
    """Nettoie les erreurs de visibilité"""
    message = re.sub(r"Locator expected to be visible", "Élément attendu visible", message)
    message = re.sub(r"Actual value:", "Valeur obtenue :", message)
    message = re.sub(r"Call log:.*", "", message)
    return message.strip()


def nettoyer_message_base(message: str) -> str:
    """Nettoyage de base pour tous les messages"""
    return (message.replace("\n", " ")
                  .replace("\r", " ")
                  .replace("\\", "/")
                  .replace('"', "'")
                  .strip())


"""
=== 4. Exemple d'utilisation ===
Test simple avec la nouvelle configuration
"""

def test_exemple_avec_verification_timeout(page, execution, etape):
    """Exemple d'utilisation - la vérification est automatique"""
    
    try:
        # Action qui peut timeout
        page.goto("https://exemple.com")
        page.wait_for_selector("button#submit", timeout=5000)
        page.click("button#submit")
        
        # Si timeout avec erreur HTTP dans la page, le système détectera :
        # "🌐 Timeout dû à une erreur HTTP - Erreur serveur (5xx) - 500 Erreur interne du serveur"
        
        # Si timeout normal, le système affichera :
        # "⏱️ Attente élément : button#submit dépassé"
        
    except Exception as e:
        # La gestion est automatique
        gestion_exception(execution, etape, page, e)


"""
=== 5. Structure des fichiers finale ===
"""

# Structure simple :
# /opt/scenarios_v6/
# ├── config/
# │   └── patterns_erreurs.yaml              # Un seul fichier de config
# ├── scenarios/
# │   ├── mon_scenario.conf
# │   └── ...
# └── ...

# Dans votre code :
# - Remplacer timeout_checker.py par verificateur_timeout.py
# - Remplacer gestion_exception.py par la version simplifiée
# - Créer le fichier patterns_erreurs.yaml

# Ajout dans src/utils/__init__.py :
# from .verificateur_timeout import VerificateurTimeout
