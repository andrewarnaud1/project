"""
Fichier généré automatiquement
Scénario: aai2_consultation_demande
Description: Consultation d'une demande dans AAI2 avec iframes par action
Généré le: 2025-07-11 09:29:06
"""


import pytest
import logging
import sys
import inspect
from playwright.sync_api import sync_playwright, Page, expect
from src.simulateur import Execution, Etape, execution, contexte, page, first_page, etape
from src.utils.screenshot_manager import take_screenshot
from src.simulateur.gestion_exception import gestion_exception
from commun import comm_portail_applicatif

class TestClass():
    """
    Les differents tests (etapes) sont regroupes dans TestClass.
    """
    def test_identification(self, execution: Execution, page: Page, etape: Etape, request):
        """
        Étape: identification
        """
        return comm_portail_applicatif.EtapesCommunes().test_identification(execution, page, etape, request)

    def test_portail_applicatif(self, execution: Execution, page: Page, etape: Etape, request):
        """
        Étape: portail_applicatif
        """
        try:
            elts_flous = []
# Action cliquer

            html_element = page.get_by_role(
                "link",
                name="AAI2",
            )
            expect(html_element).to_be_visible(timeout=30000)

            take_screenshot(execution, etape, page, elts_flous=elts_flous)
            html_element.click()

            etape.finalise(
                execution.compteur_etape,
                0,
                page.url,
                f"OK - Étape {execution.compteur_etape} portail_applicatif"
            )
            
        except Exception as e:
            gestion_exception(execution, etape, page, e)

    def test_accueil_aai2(self, execution: Execution, page: Page, etape: Etape, request):
        """
        Étape: accueil_aai2
        """
        try:
            elts_flous = []
# Action cliquer

            frame = page.frame_locator('iframe[name="iframe_principale"]')
            html_element = frame.get_by_text(
                "Demandes",
                exact=True,
            )

            expect(html_element).to_be_visible(timeout=30000)

            html_element.click()
# Action cliquer

            frame = page.frame_locator('iframe[name="iframe_principale"]')
            html_element = frame.get_by_role(
                "link",
                name="Consulter une demande",
            )
            expect(html_element).to_be_visible(timeout=30000)

            take_screenshot(execution, etape, page, elts_flous=elts_flous)
            html_element.click()

            etape.finalise(
                execution.compteur_etape,
                0,
                page.url,
                f"OK - Étape {execution.compteur_etape} accueil_aai2"
            )
            
        except Exception as e:
            gestion_exception(execution, etape, page, e)

    def test_liste_demandes(self, execution: Execution, page: Page, etape: Etape, request):
        """
        Étape: liste_demandes
        """
        try:
            elts_flous = []
# Action saisir

            frame = page.frame_locator('iframe[name="iframe_principale"]')
            html_element = frame.get_by_role(
                "textbox",
                name="Nom",
            )
            html_element.fill("test")
# Action cliquer

            frame = page.frame_locator('iframe[name="iframe_principale"]')
            html_element = frame.get_by_role(
                "button",
                name="Rechercher",
            )
            expect(html_element).to_be_visible(timeout=30000)

            take_screenshot(execution, etape, page, elts_flous=elts_flous)
            html_element.click()

            etape.finalise(
                execution.compteur_etape,
                0,
                page.url,
                f"OK - Étape {execution.compteur_etape} liste_demandes"
            )
            
        except Exception as e:
            gestion_exception(execution, etape, page, e)

    def test_resultat_recherche(self, execution: Execution, page: Page, etape: Etape, request):
        """
        Étape: resultat_recherche
        """
        try:
            elts_flous = []
# Action cliquer

            frame = page.frame_locator('iframe[name="iframe_principale"]')
            html_element = frame.get_by_role(
                "link",
                name="Visualisation de la demande",
            )
            expect(html_element).to_be_visible(timeout=30000)

            take_screenshot(execution, etape, page, elts_flous=elts_flous)
            html_element.click()

            etape.finalise(
                execution.compteur_etape,
                0,
                page.url,
                f"OK - Étape {execution.compteur_etape} resultat_recherche"
            )
            
        except Exception as e:
            gestion_exception(execution, etape, page, e)

    def test_detail_demande(self, execution: Execution, page: Page, etape: Etape, request):
        """
        Étape: detail_demande
        """
        try:
            elts_flous = []
# Action vérifier

            frame = page.frame_locator('iframe[name="iframe_principale"]')
            html_element = frame.get_by_role(
                "heading",
                name="Détail de la demande",
            )
              
            expect(html_element).to_be_visible(timeout=30000)
              

            take_screenshot(execution, etape, page, elts_flous=elts_flous)

            etape.finalise(
                execution.compteur_etape,
                0,
                page.url,
                f"OK - Étape {execution.compteur_etape} detail_demande"
            )
            
        except Exception as e:
            gestion_exception(execution, etape, page, e)

    def test_retour_portail_applicatif(self, execution: Execution, page: Page, etape: Etape, request):
        """
        Étape: retour_portail_applicatif
        """
        try:
            elts_flous = []
# Action cliquer

            html_element = page.get_by_role(
                "link",
                name="Retour vers la page d'accueil",
            )
            expect(html_element).to_be_visible(timeout=30000)

            html_element.click()
# Action vérifier

            html_element = page.get_by_role(
                "heading",
                name="Mes applications",
            )
              
            expect(html_element).to_be_visible(timeout=30000)
              

            take_screenshot(execution, etape, page, elts_flous=elts_flous)

            etape.finalise(
                execution.compteur_etape,
                0,
                page.url,
                f"OK - Étape {execution.compteur_etape} retour_portail_applicatif"
            )
            
        except Exception as e:
            gestion_exception(execution, etape, page, e)

