"""
API - Lecture des informations scéanrio et inscription des données execution
via l'api injecteurlocale
"""

import logging
import requests
import pytest

from requests.exceptions import HTTPError
from src.utils.utils import contexte_actuel

LOGGER = logging.getLogger(__name__)


def lecture_api_scenario(url_base_api_injecteur, identifiant_scenario):
    """
    Charge les données du scénario depuis l'API si la lecture est activée
    et si un identifiant est présent dans la configuration.
    """
    methode_name = contexte_actuel()
    LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

    # Vérification de la présence de l'identifiant dans la config
    # Nomalement pytest exit (lever un exception) gestion dans
    # try except supérier
    if not identifiant_scenario:
        LOGGER.error(
            "[%s]❌ Aucun identifiant de scénario trouvé dans la configuration",
            methode_name,
        )
        return  # A MODIFIER EN RAISE OU PYTEST.EXIT

    LOGGER.info(
        "[%s] Chargement des données du scénario depuis l'API (ID: %s)",
        methode_name,
        identifiant_scenario,
    )

    url = f"{url_base_api_injecteur}injapi/scenario/{identifiant_scenario}"
    LOGGER.info("[%s] url => %s", methode_name, url)

    try:
        response = requests.get(url, timeout=10)
        # Raises :class:`HTTPError`, if one occurred."""
        response.raise_for_status()
    except HTTPError as erreur:
        LOGGER.critical(
            "[%s]❌ Echec d`appel à l'API : Erreur HTTP : %s", methode_name, erreur
        )
        LOGGER.critical("[%s]❌ Reponse => %s", methode_name, erreur.response.text)
        pytest.exit(2)
    except Exception as erreur:
        LOGGER.critical("[%s]❌ Echec d`appel à l'API : %s", methode_name, erreur)
        pytest.exit(2)

    if response.json():
        LOGGER.info(
            "[%s]✅ Réponse API [%s] => %s", methode_name, response, response.text
        )
    else:
        LOGGER.critical(
            "[%s] Aucune donnée retournée par l'API : %s", methode_name, response
        )
        pytest.exit(2)

    LOGGER.debug("[%s] ----  FIN  ----", methode_name)
    return response.json()


def inscrire_resultats_api(url_base_api_injecteur: str, data: dict) -> None:
    """
    Inscrit les résultats du scénario dans l'API si l'inscription est activée.

    Args:
        data: dictionaire des données à inscrire
    """
    methode_name = contexte_actuel()
    LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

    LOGGER.info("[%s] Inscription des résultats dans l'API", methode_name)

    try:
        url = f"{url_base_api_injecteur}injapi/scenario/execution"

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/plain",
        }

        response = requests.post(url, headers=headers, timeout=10, json=data)

        response.raise_for_status()

    except HTTPError as erreur:
        LOGGER.critical(
            "[%s]❌ Inscription du scénario :Erreur HTTP => %s", methode_name, erreur
        )
        LOGGER.critical("[%s]❌ Réponse => %s", methode_name, erreur.response.text)
    except Exception as erreur:
        LOGGER.critical(
            "[%s]❌ Erreur d'inscription du scénario=> %s", methode_name, erreur
        )

    if response:
        LOGGER.info(
            "[%s]✅ Réponse API [%s] => %s", methode_name, response, response.text
        )

    LOGGER.debug("[%s] ----  FIN  ----", methode_name)


def lire_resultats_dernier_rejeux(url_base_api_injecteur, identifiant_scenario):
    """
    Charge les données du rejeu précédent depuis l'API si la lecture est activée
    et si un identifiant est présent dans la configuration.
    L'objectif est de pouvoir savoir si le dernier rejeu est vert pour la relance.
    """
    methode_name = contexte_actuel()
    LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

    # Vérification de la présence de l'identifiant dans la config
    # Nomalement pytest exit (lever un exception) gestion dans
    # try except supérier
    if not identifiant_scenario:
        LOGGER.error(
            "[%s]❌ Aucun identifiant de scénario trouvé dans la configuration",
            methode_name,
        )
        return  # TODO : A MODIFIER EN RAISE OU PYTEST.EXIT

    LOGGER.info(
        "[%s] Chargement des données du dernier rejeu depuis l'API (ID: %s)",
        methode_name,
        identifiant_scenario,
    )

    # TODO : Mettre à jour avec l'API last_execution lorsqu'elle fonctionnera
    url = f"{url_base_api_injecteur}injapi/last_execution/{identifiant_scenario}"
    LOGGER.info("[%s] url => %s", methode_name, url)

    try:
        response = requests.get(url, timeout=10)
        # Raises :class:`HTTPError`, if one occurred."""
        response.raise_for_status()
    except HTTPError as erreur:
        LOGGER.critical(
            "[%s]❌ Echec d`appel à l'API : Erreur HTTP : %s", methode_name, erreur
        )
        LOGGER.critical("[%s]❌ Reponse => %s", methode_name, erreur.response.text)
        pytest.exit(2)
    except Exception as erreur:
        LOGGER.critical("[%s]❌ Echec d`appel à l'API : %s", methode_name, erreur)
        pytest.exit(2)

    if response.json():
        LOGGER.info(
            "[%s]✅ Réponse API [%s] => %s", methode_name, response, response.text
        )
    else:
        LOGGER.critical(
            "[%s] Aucune donnée retournée par l'API : %s", methode_name, response
        )
        pytest.exit(2)

    LOGGER.debug("[%s] ----  FIN  ----", methode_name)
    return response.json()
