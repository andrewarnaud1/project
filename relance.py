"""Module de relance de scénarios."""
import logging
from src.utils.utils import contexte_actuel
from .api import lire_resultats_dernier_rejeux


LOGGER = logging.getLogger(__name__)


def relance(url_base_api_injecteur, identifiant):
    """
    Méthode qui permets de relancer le scénario en cas d'échec (KO)

    Conditions :
        - Le dernier rejeu doit être OK
        - Le rejeu actuel doit être KO

    Return:
        bool: True si le scénario doit être relancé
        sinon False.
    """
    methode_name = contexte_actuel()
    LOGGER.debug("[%s] ---- DEBUT ----", methode_name)

    # Récupération du dernier rejeu
    dernier_rejeu = lire_resultats_dernier_rejeux(
        url_base_api_injecteur=url_base_api_injecteur, identifiant_scenario=identifiant
    )

    statut_dernier_rejeu = dernier_rejeu.get('execution').get('status_inital')

    if statut_dernier_rejeu < 2:
        # Si le statut du dernier rejeu est OK il faut relancer le scénario
        return True
    else:
        # Sinon pas besoin de relancer le scénario
        return False
