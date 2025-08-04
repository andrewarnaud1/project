"""
Lance un navigateur Playwright en fonction de la configuration fournie.

Gère les navigateurs suivants :
- "chromium"
- "firefox"
- "msedge" (Chromium avec chemin d'exécutable Edge)

Les options de proxy sont gérées via la fonction `get_options_navigateur()`
du module `src.utils.navigateur` :
- None ou '' : pas de proxy
- "http://host:port" : proxy explicite
- URL .pac : script de configuration automatique

Args:
    execution.config (Dict): dictionnaire de configuration, contenant au minimum :
        - "navigateur" : type de navigateur à lancer
        - "proxy" (optionnel) : mode proxy ('', URL ou .pac)
        - "msedge_path" (optionnel) : chemin vers Edge si navigateur = "msedge"

Returns:
    Browser: instance Playwright du navigateur lancé
"""

import logging
import inspect
import pytest
from playwright.sync_api import sync_playwright
from src.utils.navigateur import (
    get_options_navigateur,
    get_http_credentials,
    get_cookies,
)
from .execution import Execution

LOGGER = logging.getLogger(__name__)

### TODO GESTION DES REPERTOIRES DE TRACE ET DE LOG AVEC LE NOM DE L'EXECUTION


@pytest.fixture(scope="session")
def contexte(execution: Execution):
    """Génération du contexte Playwright"""
    fixture_name = inspect.currentframe().f_code.co_name
    LOGGER.debug("[Fixture SETUP %s] ----  DEBUT  ----", fixture_name)
    LOGGER.debug("[Fixture SETUP %s] execution => %s", fixture_name, execution)

    navigateur = execution.config.get("navigateur", "firefox").lower()

    options_pw = get_options_navigateur(execution.config)

    LOGGER.debug("[%s] options_pw => %s", fixture_name, options_pw)

    http_credentials = get_http_credentials(execution.config)

    LOGGER.debug("[%s] http_credentials => %s", fixture_name, http_credentials)

    cookies = get_cookies(execution.config)

    LOGGER.debug("[%s] cookies => %s", fixture_name, cookies)

    with sync_playwright() as p:
        try:
            if navigateur == "chromium":
                browser = p.chromium.launch(**options_pw)

            elif navigateur == "firefox":
                browser = p.firefox.launch(**options_pw)

            elif navigateur == "msedge":
                # MS Edge = Chromium avec exécutable spécifique
                # edge_path = config.get('msedge_path', "...")
                # options["executable_path"] = edge_path
                # browser = p.chromium.launch(**options)
                raise NotImplementedError(
                    f"Le navigateur '{navigateur}' n'est pas encore supporté."
                )

            else:
                raise ValueError(f"[Playwright] Navigateur inconnu : {navigateur}")

        except Exception as erreur:
            LOGGER.fatal("❌ Echec de lancemement de playwright\n%s", erreur)
            if "BrowserType.launch: Executable doesn't exist" in (str)(erreur):
                print("Il semble que playwright n'est pas installé")
                print("ou que la variable d`environnement PLAYWRIGHT_NAVIGATEURS_PATH")
                print("ne pointe pas sur le répertoire d'installation des navigateurs")
            execution.commentaire_initial = "Erreur de lancement de playwright"
            execution.commentaire = execution.commentaire_initial
            pytest.exit(2)

        # Création d'un contexte navigateur
        # Fichier HAR pour trace réseau
        context = browser.new_context(
            ignore_https_errors=True,
            locale="fr-FR",
            http_credentials=http_credentials if bool(http_credentials) else None,
            # no_viewport=True if execution.config.get('plein_ecran') is True else False,
            viewport={ 'width': 1679, 'height': 868 }
            # record_har_path=f"{execution.config.get('report_dir')}/network_trace.har"
        )

        if cookies:
            # Ajoute les cookies au contexte
            context.add_cookies([cookies])

        # Commence l'enregistrement des traces
        context.tracing.start(
            snapshots=True, screenshots=True, title="Navigation complète"
        )
        LOGGER.debug("[Fixture SETUP %s] ----   FIN  ----", fixture_name)

        yield context

        LOGGER.debug("[FIXTURE FINAL %s] ----  DEBUT ----", fixture_name)

        # Capture finale de la trace et fermeture
        path_trace = f"{execution.config.get('report_dir')}/network_trace.zip"
        context.tracing.stop(path=path_trace)
        context.close()
        browser.close()

        LOGGER.debug("[FIXTURE FINAL %s] ----   FIN  ----", fixture_name)
