"""
Gestionnaire des erreurs.
Permets de construire le rapport avec le bon message d'erreurs.
"""

import re
import logging
import pytest
from playwright.sync_api import Page

from src.utils.utils import contexte_actuel
from src.utils.screenshot_manager import take_screenshot
from src.utils.timeout_checker import VerificateurTimeout

LOGGER = logging.getLogger(__name__)


def gestion_exception(execution, etape, page: Page, exception: Exception, etape_scenario=True):
    """Gestion des exceptions avec vérification timeout"""
    methode_name = contexte_actuel()
    LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

    # URL pour le rapport
    if len(execution.etapes) == 0:
        url = execution.config.get("url_initiale")
    else:
        url = page.url

    if etape_scenario:
        # Construire le commentaire d'erreur
        commentaire = construire_commentaire_erreur(
            etape.etape["nom"], execution, url, exception, page
        )

        LOGGER.error(" %s", commentaire)
        LOGGER.error(" Exception: %s", exception)

        etape.finalise(execution.compteur_etape, 2, url, commentaire)
    else:
        etape.finalise(execution.compteur_etape, 3, url, 'Erreur non liée au scénario', etape_scenario=etape_scenario)

    # Screenshot et sortie
    take_screenshot(execution, etape, page, erreur=True)
    LOGGER.info("[%s] Appel de pytest.exit(2)", methode_name)
    pytest.exit(2)


def construire_commentaire_erreur(
    nom_etape: str, execution, url: str, exception: Exception, page: Page
) -> str:
    """Construit le commentaire d'erreur en vérifiant la cause"""

    base_commentaire = f"KO - Etape {execution.compteur_etape} {nom_etape}"
    message_exception = str(exception)

    # Vérifier si c'est un timeout
    if est_timeout(message_exception):
        try:
            # Verifie si un timeout est du à une erreur applicative
            verificateur = VerificateurTimeout(execution.config)

            # Vérifier si des fichiers d'erreurs sont chargés
            if verificateur.patterns_charges:
                cause_timeout = verificateur.verifier_cause_timeout(page)

                if cause_timeout:
                    # Timeout causé par une erreur détectée dans la page
                    return f"{base_commentaire} : Timeout dû à une erreur - {cause_timeout}"
                else:
                    # Timeout normal avec patterns disponibles
                    message_nettoye = nettoyer_message_timeout(message_exception)
                    return f"{base_commentaire} : {message_nettoye}"
            else:
                # Aucun pattern chargé - timeout normal
                message_nettoye = nettoyer_message_timeout(message_exception)
                return f"{base_commentaire} : {message_nettoye} (Aucun fichier d'erreur disponible)"

        except Exception as e:
            # Erreur lors de la vérification - fallback vers timeout normal
            LOGGER.error(
                "[VerificateurTimeout] Erreur lors de la construction de l'erreur : %s",
                e,
            )

            LOGGER.error(
                "[VerificateurTimeout] Fallback vers timeout normal pour l'étape : %s",
                nom_etape,
            )

            message_nettoye = nettoyer_message_timeout(message_exception)
            return f"{base_commentaire} : {message_nettoye} (Erreur vérification)"
    else:
        # Autre type d'erreur
        message_nettoye = nettoyer_message_erreur(message_exception, execution, url)
        return f"{base_commentaire} : {message_nettoye}"


def est_timeout(message_exception: str) -> bool:
    """Vérifie si l'exception est un timeout"""
    mots_cles_timeout = [
        "timeout",
        "timed out",
        "exceeded",
        "délai",
        "dépassé",
        "wait_for",
        "waiting for",
        "attente",
    ]

    message_minuscule = message_exception.lower()
    return any(mot_cle in message_minuscule for mot_cle in mots_cles_timeout)


def nettoyer_message_timeout(message_exception: str) -> str:
    """Nettoie et traduit les messages de timeout"""
    message = nettoyer_message_base(message_exception)

    # Traductions spécifiques aux timeouts
    message = re.sub(r"Locator\.wait_for:", "Attente élément :", message)
    message = re.sub(r"exceeded", "dépassé", message)
    message = re.sub(r"to be visible", "visible", message)
    message = re.sub(r"Call log:.*", "", message)
    message = re.sub(r"\s+", " ", message).strip()

    return message


def nettoyer_message_erreur(message: str, execution, url: str) -> str:
    """Nettoie les messages d'erreur (fonction existante simplifiée)"""
    if "Page.goto" in message:
        return nettoyer_erreur_navigation(message, execution, url)
    elif "Locator.wait_for" in message:
        return nettoyer_erreur_attente(message)
    elif "Locator expected to be visible" in message:
        return nettoyer_erreur_visibilite(message)
    elif "APIRequestContext" in message:
        return nettoyer_message_api(message)
    else:
        return nettoyer_message_base(message)


def nettoyer_message_api(message: str):
    """Nettoie les erreurs d'API"""
    if "403 Forbidden" in message:
        if "Invalid credentials" in message:
            return "Erreur HTTP : 403 - Identifiants invalides"
        else:
            return "Erreur HTTP : 403 - Inconnue"
    else:
        return "Erreur lors de l'appele API - Inconnue"


def nettoyer_erreur_navigation(message: str, execution, url: str) -> str:
    """Nettoie les erreurs de navigation"""
    message = re.sub(r"^Page\.goto:", f"Ouverture {url} : ", message)
    message = re.sub(r"Call log:.*$", "", message, flags=re.DOTALL)

    # Traduction des codes d'erreur Firefox
    traductions = {
        "NS_ERROR_PROXY_CONNECTION_REFUSED": "Connexion au proxy refusée",
        "NS_ERROR_UNKNOWN_PROXY_HOST": "Nom d'hôte du proxy introuvable",
        "NS_ERROR_CONNECTION_REFUSED": "Connexion au serveur refusée",
        "NS_ERROR_NET_TIMEOUT": "La connexion a expiré",
        "NS_ERROR_OFFLINE": "Mode hors-ligne activé",
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
        "NS_ERROR_HTTPS_ONLY": "Rejeté (mode HTTPS-only)",
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
        "SSL_ERROR_UNKNOWN": "Echec de connexion sécurisée",
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
    message = re.sub(
        r"Locator expected to be visible", "Élément attendu visible", message
    )
    message = re.sub(r"Actual value:", "Valeur obtenue :", message)
    message = re.sub(r"Call log:.*", "", message)
    return message.strip()


def nettoyer_message_base(message: str) -> str:
    """Nettoyage de base pour tous les messages"""
    return (
        message.replace("\n", " ")
        .replace("\r", " ")
        .replace("\\", "/")
        .replace('"', "'")
        .strip()
    )
