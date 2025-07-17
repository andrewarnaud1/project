"""
=== src/utils/verificateur_timeout.py ===
Vérificateur de timeout avec gestion des fichiers multiples
"""

import logging
import re
from typing import List, Optional, Dict
from playwright.sync_api import Page
from src.utils.yaml_loader import load_yaml_file

LOGGER = logging.getLogger(__name__)

class VerificateurTimeout:
    """Vérificateur de timeout avec configuration externe multiple"""
    
    def __init__(self, config_execution: Dict):
        self.config_execution = config_execution
        self.patterns = self._charger_tous_les_patterns()
        self.patterns_charges = self.patterns is not None
    
    def _charger_tous_les_patterns(self) -> Optional[Dict]:
        """Charge tous les patterns d'erreur depuis les fichiers configurés"""
        patterns_combines = {}
        fichiers_charges = []
        
        # 1. Toujours charger le fichier commun en premier
        patterns_communs = self._charger_fichier_commun()
        if patterns_communs:
            patterns_combines = self._fusionner_patterns(patterns_combines, patterns_communs)
            fichiers_charges.append("patterns_erreurs.yaml (commun)")
            LOGGER.info("[VerificateurTimeout] Fichier commun chargé")
        else:
            LOGGER.warning("[VerificateurTimeout] ⚠️ Fichier commun introuvable - Aucune détection d'erreur HTTP")
            return None
        
        # 2. Charger les fichiers spécifiques configurés
        fichiers_specifiques = self._obtenir_fichiers_specifiques()
        if fichiers_specifiques:
            for nom_fichier in fichiers_specifiques:
                patterns_specifiques = self._charger_fichier_specifique(nom_fichier)
                if patterns_specifiques:
                    patterns_combines = self._fusionner_patterns(patterns_combines, patterns_specifiques)
                    fichiers_charges.append(f"{nom_fichier}.yaml")
                    LOGGER.info(f"[VerificateurTimeout] Fichier spécifique {nom_fichier} chargé")
                else:
                    LOGGER.warning(f"[VerificateurTimeout] ⚠️ Fichier spécifique {nom_fichier} introuvable")
        
        # 3. Afficher un résumé des fichiers chargés
        if fichiers_charges:
            LOGGER.info(f"[VerificateurTimeout] Fichiers chargés: {', '.join(fichiers_charges)}")
        
        return patterns_combines
    
    def _charger_fichier_commun(self) -> Optional[Dict]:
        """Charge le fichier de patterns commun"""
        try:
            simu_scenarios = self.config_execution.get('simu_scenarios', '/opt/scenarios_v6')
            chemin_fichier_commun = f"{simu_scenarios}/config/patterns_erreurs.yaml"
            
            return load_yaml_file(chemin_fichier_commun)
        except Exception as e:
            LOGGER.debug(f"[VerificateurTimeout] Erreur chargement fichier commun: {e}")
            return None
    
    def _obtenir_fichiers_specifiques(self) -> List[str]:
        """Récupère la liste des fichiers spécifiques depuis la configuration"""
        # Chercher dans la configuration sous la clé 'fichiers_patterns_erreurs'
        fichiers_specifiques = self.config_execution.get('fichiers_patterns_erreurs', [])
        
        # S'assurer que c'est une liste
        if isinstance(fichiers_specifiques, str):
            fichiers_specifiques = [fichiers_specifiques]
        elif not isinstance(fichiers_specifiques, list):
            fichiers_specifiques = []
        
        LOGGER.debug(f"[VerificateurTimeout] Fichiers spécifiques configurés: {fichiers_specifiques}")
        return fichiers_specifiques
    
    def _charger_fichier_specifique(self, nom_fichier: str) -> Optional[Dict]:
        """Charge un fichier de patterns spécifique"""
        try:
            simu_scenarios = self.config_execution.get('simu_scenarios', '/opt/scenarios_v6')
            
            # Ajouter l'extension .yaml si pas présente
            if not nom_fichier.endswith('.yaml'):
                nom_fichier = f"{nom_fichier}.yaml"
            
            chemin_fichier = f"{simu_scenarios}/config/{nom_fichier}"
            
            return load_yaml_file(chemin_fichier)
        except Exception as e:
            LOGGER.debug(f"[VerificateurTimeout] Erreur chargement fichier {nom_fichier}: {e}")
            return None
    
    def _fusionner_patterns(self, patterns_base: Dict, nouveaux_patterns: Dict) -> Dict:
        """Fusionne deux dictionnaires de patterns"""
        if not patterns_base:
            return nouveaux_patterns.copy()
        
        # Fusion simple avec l'opérateur | (Python 3.9+)
        # ou patterns_base.copy().update(nouveaux_patterns) pour Python < 3.9
        return patterns_base | nouveaux_patterns
    
    def verifier_cause_timeout(self, page: Page) -> Optional[str]:
        """
        Vérifie si un timeout est causé par une erreur HTTP
        
        Returns:
            str: Message d'erreur HTTP ou None si pas d'erreur ou pas de patterns
        """
        # Si aucun pattern n'est chargé, ne pas faire de recherche
        if not self.patterns_charges:
            LOGGER.debug("[VerificateurTimeout] Aucun pattern chargé - Pas de vérification HTTP")
            return None
        
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
=== src/gestion_exception.py ===
Gestionnaire d'exception modifié
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
        
        # Vérifier si des patterns sont chargés
        if verificateur.patterns_charges:
            cause_timeout = verificateur.verifier_cause_timeout(page)
            
            if cause_timeout:
                # Timeout causé par une erreur HTTP
                return f"{base_commentaire} : 🌐 Timeout dû à une erreur HTTP - {cause_timeout}"
            else:
                # Timeout normal avec patterns disponibles
                message_nettoye = nettoyer_message_timeout(message_exception)
                return f"{base_commentaire} : ⏱️ {message_nettoye}"
        else:
            # Aucun pattern chargé - timeout normal avec alerte
            message_nettoye = nettoyer_message_timeout(message_exception)
            return f"{base_commentaire} : ⏱️ {message_nettoye} (⚠️ Aucun pattern d'erreur HTTP disponible)"
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
=== Exemple de configuration dans un fichier scenario.conf ===
"""

# Dans votre fichier de configuration de scénario (ex: adonis_login.conf)
# Exemple 1: Aucun fichier spécifique (utilise seulement le fichier commun)
# identifiant: "adonis_login_001"
# navigateur: "firefox"
# ... autres paramètres ...

# Exemple 2: Un seul fichier spécifique
# identifiant: "adonis_login_001"
# navigateur: "firefox"
# fichiers_patterns_erreurs: "patterns_erreurs_adonis"
# ... autres paramètres ...

# Exemple 3: Plusieurs fichiers spécifiques
# identifiant: "gestpas_search_001"
# navigateur: "firefox"
# fichiers_patterns_erreurs:
#   - "patterns_erreurs_gestpas"
#   - "patterns_erreurs_dgfip"
#   - "patterns_erreurs_common_apps"
# ... autres paramètres ...

# Exemple 4: Fichier spécifique avec extension
# identifiant: "custom_app_001"
# navigateur: "firefox"
# fichiers_patterns_erreurs: "patterns_erreurs_custom.yaml"
# ... autres paramètres ...


"""
=== Structure des fichiers attendue ===
"""

# /opt/scenarios_v6/config/
# ├── patterns_erreurs.yaml                    # Fichier commun (OBLIGATOIRE)
# ├── patterns_erreurs_adonis.yaml             # Spécifique à Adonis
# ├── patterns_erreurs_gestpas.yaml            # Spécifique à Gestpas
# ├── patterns_erreurs_dgfip.yaml              # Spécifique à DGFIP
# ├── patterns_erreurs_common_apps.yaml        # Commun à plusieurs apps
# └── patterns_erreurs_custom.yaml             # Personnalisé

"""
=== Logs d'exemple ===
"""

# Configuration sans fichier spécifique :
# [VerificateurTimeout] Fichier commun chargé
# [VerificateurTimeout] Fichiers spécifiques configurés: []
# [VerificateurTimeout] Fichiers chargés: patterns_erreurs.yaml (commun)

# Configuration avec fichiers spécifiques :
# [VerificateurTimeout] Fichier commun chargé
# [VerificateurTimeout] Fichiers spécifiques configurés: ['patterns_erreurs_adonis', 'patterns_erreurs_dgfip']
# [VerificateurTimeout] Fichier spécifique patterns_erreurs_adonis chargé
# [VerificateurTimeout] Fichier spécifique patterns_erreurs_dgfip chargé
# [VerificateurTimeout] Fichiers chargés: patterns_erreurs.yaml (commun), patterns_erreurs_adonis.yaml, patterns_erreurs_dgfip.yaml

# Fichier commun introuvable :
# [VerificateurTimeout] ⚠️ Fichier commun introuvable - Aucune détection d'erreur HTTP
# [VerificateurTimeout] Aucun pattern chargé - Pas de vérification HTTP
# Timeout message: "⏱️ Attente élément : button#submit dépassé (⚠️ Aucun pattern d'erreur HTTP disponible)"
