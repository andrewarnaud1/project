import logging
import json
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def get_options_navigateur(config: dict) -> dict:
    """
    Génère les options Playwright à partir de la configuration donnée.
    Gère la configuration du proxy :
    - None ou '' : pas de proxy
    - host:port : proxy explicite
    - http(s)://... .pac : proxy automatique via script

    Args:
        config (dict): dictionnaire de configuration, doit contenir "proxy"

    Returns:
        dict: options à passer à launch() de Playwright
    """
    options = {}
    navigateur = config.get("navigateur")

    plein_ecran = config.get("plein_ecran")

    if plein_ecran is True:
        options['args'] = ['--start-maximized']

    # Sans tête !
    options["headless"] = config.get("headless", True)

    # gestion du proxy
    proxy_config = config.get("proxy", "").strip().lower()

    # Firefox prefs
    if navigateur == "firefox" and proxy_config.endswith(".pac"):
        options["firefox_user_prefs"] = {
            "extensions.formautofill.creditCards.supported": "off",
            "extensions.formautofill.addresses.supported": "off",
            "dom.push.serverURL": "",
            #         'security.enterprise_roots.enabled': 'true',
            #         'prompts.contentPromptSubDialog': 'false',
        }

        if proxy_config is not None and proxy_config != "":
            options["firefox_user_prefs"]["network.proxy.autoconfig_url"] = proxy_config
            options["firefox_user_prefs"]["network.proxy.type"] = 2

    else:
        if proxy_config == "":
            pass

        elif proxy_config.endswith(".pac"):
            options["proxy"] = {"server": "per-context", "pac": proxy_config}

        else:
            options["proxy"] = {"server": proxy_config}

    return options


def get_http_credentials(config: dict) -> dict:
    """
    Fonction qui permets de récupérer les identifiants
    de connexion http pour les ajouter au paramètres du navigateur.
    """
    http_credentials = {}

    if config.get("http_credentials"):
        http_credentials["username"] = config.get("http_credentials").get("utilisateur")
        http_credentials["password"] = config.get("http_credentials").get(
            "mot_de_passe"
        )

    return http_credentials


def get_cookies(config: dict):
    """
    Fonction qui permets de retourner le fichier de cookies
    afin de les ajouter au contexte du navigateur.
    """
    if config.get("cookies"):
        # Chemin relatif du fichier de configs browser
        cookies_file_path = f"{config.get('scenarios_path')}/cookies/" + str(
            f"{config.get('cookies')}.json"
        )

        # Convertir le str en un path
        cookies_file_path = Path(cookies_file_path)

        # Vérifie si un fichier de cookies associé au scénario existe
        if Path(cookies_file_path).exists():
            # Ouverture du fichier de cookies
            with open(cookies_file_path, "r") as fichier_cookies:
                return json.load(fichier_cookies)
    else:
        return None
