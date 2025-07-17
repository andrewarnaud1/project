"""
=== 1. src/utils/timeout_checker.py ===
Vérificateur simple pour les timeouts avec analyse HTML
"""

import logging
from typing import List, Optional
from playwright.sync_api import Page

LOGGER = logging.getLogger(__name__)

class TimeoutChecker:
    """Vérificateur simple des timeouts avec analyse HTML"""
    
    @staticmethod
    def check_timeout_cause(page: Page) -> Optional[str]:
        """
        Vérifie si un timeout est causé par une erreur HTTP visible dans le HTML
        
        Returns:
            str: Message d'erreur HTTP trouvé ou None si pas d'erreur détectée
        """
        try:
            # Chercher les erreurs HTTP dans la page principale et toutes les frames
            error_messages = TimeoutChecker._find_http_errors_in_all_frames(page)
            
            if error_messages:
                return f"Erreur HTTP détectée: {error_messages[0]}"
            
            return None
            
        except Exception as e:
            LOGGER.debug(f"[TimeoutChecker] Erreur lors de la vérification: {e}")
            return None
    
    @staticmethod
    def _find_http_errors_in_all_frames(page: Page) -> List[str]:
        """Cherche les erreurs HTTP dans la page et toutes ses frames"""
        all_errors = []
        
        # Chercher dans la page principale
        main_errors = TimeoutChecker._extract_http_errors_from_html(page)
        all_errors.extend(main_errors)
        
        # Chercher dans toutes les frames
        for frame in page.frames:
            if frame != page.main_frame:
                try:
                    frame_errors = TimeoutChecker._extract_http_errors_from_html(frame)
                    all_errors.extend(frame_errors)
                except Exception as e:
                    LOGGER.debug(f"[TimeoutChecker] Erreur frame {frame.url}: {e}")
                    continue
        
        # Supprimer les doublons et retourner
        return list(set(all_errors))
    
    @staticmethod
    def _extract_http_errors_from_html(page_or_frame) -> List[str]:
        """Extrait les erreurs HTTP du contenu HTML"""
        errors = []
        
        try:
            # Récupérer le contenu HTML complet
            html_content = page_or_frame.content()
            
            # Rechercher les codes d'erreur HTTP courants
            http_errors = TimeoutChecker._search_http_codes_in_html(html_content)
            errors.extend(http_errors)
            
            # Rechercher les messages d'erreur dans les éléments visibles
            visible_errors = TimeoutChecker._search_visible_error_messages(page_or_frame)
            errors.extend(visible_errors)
            
        except Exception as e:
            LOGGER.debug(f"[TimeoutChecker] Erreur extraction HTML: {e}")
        
        return errors
    
    @staticmethod
    def _search_http_codes_in_html(html_content: str) -> List[str]:
        """Cherche les codes d'erreur HTTP dans le contenu HTML"""
        import re
        
        errors = []
        html_lower = html_content.lower()
        
        # Patterns pour les codes d'erreur HTTP
        error_patterns = [
            # Codes d'erreur explicites
            r'(error|erreur)\s*(40[0-9]|50[0-9])',
            r'(40[0-9]|50[0-9])\s*(error|erreur)',
            
            # Messages d'erreur spécifiques
            r'404.*not found',
            r'500.*internal server error',
            r'502.*bad gateway',
            r'503.*service unavailable',
            r'504.*gateway timeout',
            
            # Messages en français
            r'erreur\s*(40[0-9]|50[0-9])',
            r'(40[0-9]|50[0-9]).*erreur',
            r'page.*introuvable',
            r'serveur.*indisponible',
            r'erreur.*serveur',
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, html_lower)
            if matches:
                # Extraire le contexte autour de l'erreur
                for match in matches[:3]:  # Max 3 matches
                    match_str = match if isinstance(match, str) else ' '.join(match)
                    errors.append(f"Code HTTP: {match_str}")
        
        return errors
    
    @staticmethod
    def _search_visible_error_messages(page_or_frame) -> List[str]:
        """Cherche les messages d'erreur dans les éléments visibles"""
        errors = []
        
        # Sélecteurs pour les messages d'erreur courants
        error_selectors = [
            'h1:has-text("404")',
            'h1:has-text("500")',
            'h1:has-text("Error")',
            'h1:has-text("Erreur")',
            
            # Éléments avec classes d'erreur
            '.error:visible',
            '.erreur:visible',
            '.alert-error:visible',
            '.alert-danger:visible',
            '.message-error:visible',
            
            # Éléments avec IDs d'erreur
            '#error:visible',
            '#erreur:visible',
            '#error-message:visible',
            
            # Texte contenant des mots-clés d'erreur
            ':text("Internal Server Error")',
            ':text("Not Found")',
            ':text("Service Unavailable")',
            ':text("Bad Gateway")',
            ':text("Gateway Timeout")',
            
            # Français
            ':text("Erreur du serveur")',
            ':text("Page introuvable")',
            ':text("Service indisponible")',
            ':text("Erreur interne")',
        ]
        
        for selector in error_selectors:
            try:
                elements = page_or_frame.locator(selector).all()
                for element in elements:
                    try:
                        text = element.inner_text(timeout=1000).strip()
                        if text and len(text) > 3:
                            errors.append(text[:100])  # Limiter à 100 caractères
                            if len(errors) >= 3:  # Max 3 messages
                                break
                    except:
                        continue
            except:
                continue
        
        return errors


"""
=== 2. src/gestion_exception.py ===
Modification simple de votre gestionnaire existant
"""

import re
import logging
import pytest

from src.utils.utils import contexte_actuel
from src.utils.screenshot_manager import take_screenshot
from src.utils.timeout_checker import TimeoutChecker

LOGGER = logging.getLogger(__name__)

def gestion_exception(execution, etape, page, exception: Exception):
    '''Gestion des exceptions avec vérification timeout'''
    methode_name = contexte_actuel()
    LOGGER.debug('[%s] ---- DEBUT ----', methode_name)
    LOGGER.debug('[%s] type(e).__name__ => %s', methode_name, type(exception).__name__)
    LOGGER.debug('[%s] Exception => %s', methode_name, exception)
    
    # Pour la première page, l'url est "about:blank" => url_initiale !
    if len(execution.etapes) == 0:
        url = execution.config.get('url_initiale')
    else:
        url = page.url

    # Vérifier si c'est un timeout et analyser la cause
    commentaire = construire_commentaire(etape.etape['nom'], execution, url, exception, page)
    
    LOGGER.error(f"❌{commentaire}")
    LOGGER.error(f"❌{exception}")
    
    etape.finalise(execution.compteur_etape, 2, url, commentaire)

    # screenshot et sortie
    take_screenshot(execution, etape, page, erreur=True)
    LOGGER.info('[%s] Appel de pytest.exit(2)', methode_name)
    pytest.exit(2)
    LOGGER.debug('[%s] ----  FIN  ----', methode_name)


def construire_commentaire(nom_etape, execution, url, exception, page):
    '''Construction du commentaire avec vérification timeout'''
    exception_str = str(exception)
    
    # Vérifier si c'est un timeout
    if is_timeout_error(exception_str):
        # Vérifier la cause du timeout
        timeout_cause = TimeoutChecker.check_timeout_cause(page)
        
        if timeout_cause:
            # Timeout causé par une erreur HTTP
            message = f"Timeout dû à une erreur HTTP - {timeout_cause}"
            commentaire = f"KO - Etape {execution.compteur_etape} {nom_etape} : 🌐 {message}"
        else:
            # Timeout normal (élément pas trouvé, etc.)
            message = traduire_timeout_normal(exception_str)
            commentaire = f"KO - Etape {execution.compteur_etape} {nom_etape} : ⏱️ {message}"
    else:
        # Pas un timeout - traitement normal
        message = traduire_erreur(exception_str, execution, url)
        commentaire = f"KO - Etape {execution.compteur_etape} {nom_etape} : {message}"
    
    return commentaire


def is_timeout_error(exception_str: str) -> bool:
    """Vérifie si l'exception est un timeout"""
    timeout_keywords = [
        'timeout', 'timed out', 'exceeded', 'délai', 'dépassé',
        'wait_for', 'waiting for', 'attente'
    ]
    
    exception_lower = exception_str.lower()
    return any(keyword in exception_lower for keyword in timeout_keywords)


def traduire_timeout_normal(exception_str: str) -> str:
    """Traduit les messages de timeout normaux"""
    message = nettoyer_message(exception_str)
    
    # Traductions spécifiques aux timeouts
    message = re.sub(r'Locator\.wait_for:', 'Attente élément :', message)
    message = re.sub(r'exceeded', 'dépassé', message)
    message = re.sub(r'to be visible', 'visible', message)
    message = re.sub(r'Call log:.*', '', message)
    message = re.sub(r'\s+', ' ', message).strip()
    
    return message


def traduire_erreur(message, execution, url):
    '''Traduction des messages d'erreur (code existant)'''
    msg_erreur = message
    
    if 'Page.goto' in message:
        msg_erreur = erreur_page_goto(message, execution, url)
    elif 'Locator.wait_for' in message:
        msg_erreur = erreur_attente_element(message, execution, url)
    elif 'Locator expected to be visible' in message:
        msg_erreur = erreur_assert_element(message, execution, url)
    
    # suppression des espaces doubles
    msg_erreur = re.sub(r'\s+', ' ', msg_erreur)
    
    return msg_erreur


def nettoyer_message(message: str) -> str:
    """Nettoie un message pour le rendre compatible avec le format JSON."""
    return (message.replace("\n", " ")
                  .replace("\r", " ")
                  .replace("\\", "/")
                  .replace('"', "'")
                  .strip())


def erreur_page_goto(message, execution, url):
    """Gestion des erreurs Page.goto (code existant)"""
    ERRORS = {
        "NS_ERROR_PROXY_CONNECTION_REFUSED": "Connexion au proxy refusée",
        "NS_ERROR_UNKNOWN_PROXY_HOST": "Nom d'hôte du proxy introuvable",
        "NS_ERROR_CONNECTION_REFUSED": "Connexion au serveur refusée",
        "NS_ERROR_NET_TIMEOUT": "La connexion a expiré",
        "NS_ERROR_OFFLINE": "Mode hors‑ligne activé",
        "NS_ERROR_NET_RESET": "Connexion établie, aucune donnée reçue",
        "NS_ERROR_NET_INTERRUPT": "Transfert interrompu",
        "NS_ERROR_DNS_LOOKUP_QUEUE_FULL": "File DNS pleine",
        "NS_ERROR_UNKNOWN_HOST": "Nom d'hôte introuvable",
        "NS_ERROR_REDIRECT_LOOP": "Boucle de redirection détectée",
        "NS_ERROR_NET_PARTIAL_TRANSFER": "Transfert partiel terminé",
        "NS_ERROR_NET_INADEQUATE_SECURITY": "Sécurité HTTP/2/TLS insuffisante",
        "NS_ERROR_NET_HTTP2_SENT_GOAWAY": "HTTP/2 GOAWAY reçu",
        "NS_ERROR_NET_HTTP3_PROTOCOL_ERROR": "Erreur protocole HTTP/3",
        "NS_ERROR_NET_TIMEOUT_EXTERNAL": "Timeout externe détecté",
        "NS_ERROR_HTTPS_ONLY": "Rejeté (mode HTTPS‑only)",
        "NS_ERROR_WEBSOCKET_CONNECTION_REFUSED": "WebSocket refusé",
        "NS_ERROR_NON_LOCAL_CONNECTION_REFUSED": "Connexion locale interdite",
        "NS_ERROR_BAD_HSTS_CERT": "Certificat HSTS invalide",
        "NS_ERROR_PARSING_HTTP_STATUS_LINE": "Erreur ligne de statut HTTP",
        "NS_ERROR_SUPERFLUOS_AUTH": "Authentification superflue bloquée",
        "NS_ERROR_BASIC_HTTP_AUTH_DISABLED": "Auth basique HTTP désactivée",
        "NS_ERROR_LOCAL_NETWORK_ACCESS_DENIED": "Accès réseau local refusé",
        "NS_ERROR_SOCKET_CREATE_FAILED": "Échec création socket",
        "NS_ERROR_UNKNOWN_PROTOCOL": "Protocole URI inconnu",
        "NS_ERROR_MALFORMED_URI": "URI mal formée",
        "NS_ERROR_IN_PROGRESS": "Opération déjà en cours",
        "NS_ERROR_PORT_ACCESS_NOT_ALLOWED": "Port non autorisé",
        "SSL_ERROR_UNKNOWN": "Echec de connexion sécurisée"
    }

    message = re.sub(r"^Page\.goto:", f"Ouverture {url} : ", message)
    message = re.sub(r"Call log:.*navigating to '.*?'\,.*$", "", message)
    message = message.strip()

    for code, trad in ERRORS.items():
        message = re.sub(rf"\b{code}\b", trad, message)

    if 'proxy' in message:
        message = message + f" ({execution.config.get('proxy')})"
    
    return message


def erreur_attente_element(message, execution, url):
    """Gestion des erreurs d'attente d'élément (code existant)"""
    message = re.sub(r"^Locator.wait_for:", "Attente élément : ", message)
    message = re.sub(r"exceeded", "dépassé", message)
    message = re.sub(r"Call log:   - waiting for get_by_role", "", message)
    message = re.sub(r"to be visible", "n'est pas visible", message)
    return message


def erreur_assert_element(message, execution, url):
    """Gestion des erreurs d'assertion d'élément (code existant)"""
    message = re.sub(
        r"Locator expected to be visible Actual value:",
         "Sélecteur attendu comme visible, valeur obtenue : ",
          message)
    message = re.sub(
        r"  Call log:   - LocatorAssertions.to_be_visible with ",
         "(",
          message)
    message = re.sub(
        r"   - waiting for get_by_role",
         ") - Attente de ",
          message)
    message = message + '.'
    return message


"""
=== 3. Exemple d'utilisation ===
Test avec gestion automatique
"""

def test_exemple_avec_timeout_check(page, execution, etape):
    """Exemple d'utilisation - la vérification est automatique"""
    
    try:
        # Action qui peut timeout
        page.goto("https://exemple.com")
        page.wait_for_selector("button#submit", timeout=5000)
        page.click("button#submit")
        
        # Si timeout, gestion_exception() vérifiera automatiquement
        # s'il y a une erreur HTTP dans la page
        
    except Exception as e:
        # Le gestionnaire fait automatiquement la vérification
        gestion_exception(execution, etape, page, e)


"""
=== 4. Ajout dans votre __init__.py ===
Import du nouveau module
"""

# Dans src/utils/__init__.py, ajoutez:
from .timeout_checker import TimeoutChecker
