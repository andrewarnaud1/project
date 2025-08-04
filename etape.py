"""Gestion des Etapes d'un scenario"""

import time
from datetime import datetime
import logging
import inspect
import pytest
from playwright.sync_api import sync_playwright

from src.utils.utils import contexte_actuel

LOGGER = logging.getLogger(__name__)


class Etape:
    """Gestion des étapes d'une execution (instance de test de scenario)"""

    def __init__(self, request):
        """Création d'une etape."""

        LOGGER.info("Etape [%s] ---- DEBUT ----", request.node.name[5:])
        # TODO Gestion du numero d'etape
        self.etape = {
            "nom": request.node.name[5:],
            "ordre": "",
            "date": datetime.now().isoformat(),  # '%Y-%m-%dT%H:%M:%S'
            "duree": 0,
            "status": 3,
            "url": "",
            "commentaire": "",
            "start": time.time(),  # Pour calculer la duree
        }
        self.compteur_screenshot = 0
        LOGGER.debug(
            "[%s] etape créée => %s", inspect.currentframe().f_code.co_name, self.etape
        )

    def __str__(self):
        return f"{self.etape}"

    def set_ordre(self, ordre):
        """Récupération du numéro de l'étape"""
        self.etape["ordre"] = ordre

    def set_duree(self):
        """Calcul de la durée de l'étape"""
        duree = time.time() - self.etape["start"]
        # enregiste la duree sous forme de chaine (seconde avec précision au milieme)
        self.etape["duree"] = f"{duree:.3f}"

    def set_status(self, status):
        """Récupération du statut de l'étape"""
        self.etape["status"] = status

    def set_url(self, url):
        """Récupération de l'url de l'étape"""
        self.etape["url"] = url

    def set_commentaire(self, commentaire):
        """Récupération du commentaire de l'étape"""
        self.etape["commentaire"] = commentaire

    def finalise(self, ordre, status, url, commentaire, etape_scenario=True):
        """Calculs d'une fin d'étape"""
        if etape_scenario:
            self.set_ordre(ordre)
            self.set_status(status)
            self.set_duree()

        self.set_url(url)
        self.set_commentaire(commentaire)
        
        if self.etape["status"] == 0:
            LOGGER.info("✅ %s", commentaire)
        elif self.etape["status"] == 1:
            LOGGER.warning("⚠️ %s", commentaire)
        else:
            LOGGER.error("❌ %s", commentaire)
        LOGGER.info("Etape [%s] ----  FIN  ----", self.etape["nom"])


@pytest.fixture(scope="function")
def etape(execution, request):
    """
    Pemret de générer la page à partir du contexte
    """
    fixture_name = inspect.currentframe().f_code.co_name
    LOGGER.debug("[Fixture SETUP %s] ----  DEBUT  ----", fixture_name)
    etape = Etape(request)
    execution.compteur_etape += 1
    LOGGER.debug("[Fixture SETUP %s] ----   FIN  ----", fixture_name)

    yield etape

    LOGGER.debug("[Fixture FINAL %s] ----  DEBUT ----", fixture_name)
    execution.ajoute_etape(etape.etape)
    LOGGER.debug(
        "[Fixture FINAL %s] (%s)etapes => %s ",
        fixture_name,
        type(execution.etapes),
        execution.etapes,
    )
    LOGGER.debug("[Fixture FINAL %s] ----   FIN  ----", fixture_name)
