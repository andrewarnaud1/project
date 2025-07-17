import logging
import re
from typing import List, Optional
from playwright.sync_api import Page

LOGGER = logging.getLogger(__name__)

class TimeoutChecker:
    """Vérificateur simple des timeouts avec analyse HTML corrigée"""
    
    @staticmethod
    def check_timeout_cause(page: Page) -> Optional[str]:
        """
        Vérifie si un timeout est causé par une erreur HTTP visible dans le HTML
        
        Returns:
            str: Message d'erreur HTTP trouvé ou None si pas d'erreur détectée
        """
        try:
            # Chercher les erreurs HTTP dans la page principale et toutes les frames
            error_info = TimeoutChecker._find_http_errors_in_all_frames(page)
            
            if error_info:
                return error_info[0]  # Retourner la première erreur trouvée
            
            return None
            
        except Exception as e:
            LOGGER.debug(f"[TimeoutChecker] Erreur lors de la vérification: {e}")
            return None
    
    @staticmethod
    def get_error_type(error_code: int) -> str:
        """
        Détermine le type d'erreur HTTP
        
        Returns:
            str: Type d'erreur (4xx, 5xx, etc.)
        """
        if 400 <= error_code <= 499:
            return "4xx"
        elif 500 <= error_code <= 599:
            return "5xx"
        elif 300 <= error_code <= 399:
            return "3xx"
        else:
            return "autre"
    
    @staticmethod
    def format_error_message(error_code: int, context: str = "") -> str:
        """
        Formate un message d'erreur avec le type et la description
        
        Args:
            error_code: Code d'erreur HTTP
            context: Contexte supplémentaire
            
        Returns:
            str: Message formaté
        """
        error_type = TimeoutChecker.get_error_type(error_code)
        
        # Descriptions des types d'erreur
        type_descriptions = {
            "4xx": "Erreur client",
            "5xx": "Erreur serveur", 
            "3xx": "Redirection",
            "autre": "Erreur inconnue"
        }
        
        # Descriptions spécifiques des codes courants
        code_descriptions = {
            400: "Bad Request",
            401: "Non autorisé",
            403: "Accès interdit",
            404: "Page non trouvée",
            405: "Méthode non autorisée",
            408: "Timeout de la requête",
            429: "Trop de requêtes",
            500: "Erreur interne du serveur",
            501: "Non implémenté",
            502: "Mauvaise passerelle",
            503: "Service indisponible",
            504: "Timeout de la passerelle",
            505: "Version HTTP non supportée"
        }
        
        type_desc = type_descriptions.get(error_type, "Erreur")
        code_desc = code_descriptions.get(error_code, "")
        
        if code_desc:
            message = f"{type_desc} ({error_type}) - {error_code} {code_desc}"
        else:
            message = f"{type_desc} ({error_type}) - Code {error_code}"
        
        if context:
            message += f" - {context}"
        
        return message
    
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
            
            # Recherche directe dans le HTML brut
            html_errors = TimeoutChecker._search_in_html_content(html_content)
            errors.extend(html_errors)
            
            # Recherche dans les éléments visibles pour compléter
            visible_errors = TimeoutChecker._search_in_visible_elements(page_or_frame)
            errors.extend(visible_errors)
            
        except Exception as e:
            LOGGER.debug(f"[TimeoutChecker] Erreur extraction HTML: {e}")
        
        return errors
    
    @staticmethod
    def _search_in_html_content(html_content: str) -> List[str]:
        """Recherche directe dans le contenu HTML avec détection du type d'erreur"""
        errors = []
        
        # Patterns pour détecter les codes d'erreur HTTP dans le HTML
        code_patterns = [
            # Error code: 500, 404, etc.
            r'error\s*code\s*:\s*([45]\d{2})',
            r'code\s*erreur\s*:\s*([45]\d{2})',
            
            # data-l10n-args avec responsestatus
            r'data-l10n-args="[^"]*responsestatus[^"]*:([45]\d{2})',
            r'responsestatus[^"]*:([45]\d{2})',
            
            # HTTP/1.1 500, Status: 404, etc.
            r'http/1\.[01]\s+([45]\d{2})',
            r'status\s*:\s*([45]\d{2})',
            r'response\s*:\s*([45]\d{2})',
        ]
        
        # Messages d'erreur génériques (sans code spécifique)
        generic_patterns = [
            r'internal\s*server\s*error',
            r'not\s*found.*404',
            r'service\s*unavailable',
            r'bad\s*gateway',
            r'gateway\s*timeout',
            r'erreur\s*du\s*serveur',
            r'page\s*introuvable',
            r'service\s*indisponible',
            r'erreur\s*interne',
            r'looks\s*like.*problem.*site',
            r'problème.*site',
        ]
        
        html_lower = html_content.lower()
        
        # 1. Chercher les codes d'erreur spécifiques
        for pattern in code_patterns:
            matches = re.finditer(pattern, html_lower, re.IGNORECASE)
            for match in matches:
                if match.groups():
                    error_code = int(match.group(1))
                    formatted_error = TimeoutChecker.format_error_message(error_code)
                    errors.append(formatted_error)
                    
                    # Limiter à 2 erreurs avec code spécifique
                    if len(errors) >= 2:
                        return errors
        
        # 2. Si pas de code spécifique trouvé, chercher les messages génériques
        if not errors:
            for pattern in generic_patterns:
                matches = re.finditer(pattern, html_lower, re.IGNORECASE)
                for match in matches:
                    matched_text = match.group(0)
                    if 'server' in matched_text or 'serveur' in matched_text:
                        errors.append("Erreur serveur (5xx) - Type exact non déterminé")
                    elif 'not found' in matched_text or 'introuvable' in matched_text:
                        errors.append("Erreur client (4xx) - Page non trouvée")
                    elif 'unavailable' in matched_text or 'indisponible' in matched_text:
                        errors.append("Erreur serveur (5xx) - Service indisponible")
                    elif 'problem' in matched_text or 'problème' in matched_text:
                        errors.append("Erreur HTTP détectée - Type non déterminé")
                    
                    # Limiter à 1 erreur générique
                    if len(errors) >= 1:
                        break
        
        return errors
    
    @staticmethod
    def _search_in_visible_elements(page_or_frame) -> List[str]:
        """Recherche dans les éléments visibles avec détection du type d'erreur"""
        errors = []
        
        try:
            # Chercher des éléments spécifiques qui peuvent contenir des codes d'erreur
            error_elements = [
                '#errorShortDesc',
                '#response-status-label',
                '.title-text',
                'h1',
                '[data-l10n-id*="error"]',
                '[data-l10n-id*="neterror"]',
            ]
            
            for selector in error_elements:
                try:
                    elements = page_or_frame.locator(selector).all()
                    for element in elements:
                        try:
                            text = element.inner_text(timeout=500).strip()
                            if text:
                                # Chercher les codes d'erreur dans le texte
                                error_codes = re.findall(r'([45]\d{2})', text)
                                if error_codes:
                                    error_code = int(error_codes[0])
                                    formatted_error = TimeoutChecker.format_error_message(
                                        error_code, f"détecté dans {selector}"
                                    )
                                    errors.append(formatted_error)
                                elif any(keyword in text.lower() for keyword in ['error', 'problem', 'erreur', 'problème']):
                                    # Déterminer le type d'erreur basé sur le contenu
                                    if any(keyword in text.lower() for keyword in ['server', 'serveur', 'internal']):
                                        errors.append(f"Erreur serveur (5xx) - {text[:50]}...")
                                    elif any(keyword in text.lower() for keyword in ['not found', 'introuvable', 'forbidden']):
                                        errors.append(f"Erreur client (4xx) - {text[:50]}...")
                                    else:
                                        errors.append(f"Erreur HTTP - {text[:50]}...")
                        except:
                            continue
                except:
                    continue
        
        except Exception as e:
            LOGGER.debug(f"[TimeoutChecker] Erreur éléments visibles: {e}")
        
        return errors[:2]  # Max 2 erreurs depuis les éléments visibles
