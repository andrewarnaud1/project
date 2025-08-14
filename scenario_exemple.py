"""
Scénario: aai2_consultation_demande
Description: Consultation d'une demande dans AAI2 avec iframes par action
Architecture: Simulateur v6 Refactorisé
Migré le: 2025-01-XX
"""

import pytest
from playwright.sync_api import expect
from src.core import ScenarioPage, StepResult
from commun import comm_portail_applicatif


class TestAAI2ConsultationDemande:
    """
    Scénario de consultation d'une demande dans AAI2.
    
    Flux fonctionnel:
        1. Identification sur le portail
        2. Accès à l'application AAI2
        3. Navigation vers consultation des demandes
        4. Recherche d'une demande par nom
        5. Consultation du détail
        6. Retour au portail
    """

    def test_identification(self, page: ScenarioPage, step_result: StepResult):
        """
        Identification sur le portail applicatif.
        
        Étape commune réutilisée pour l'authentification.
        """
        # Délégation vers module commun avec nouvelles signatures
        comm_portail_applicatif.EtapesCommunes().identification(page, step_result)

    def test_portail_applicatif(self, page: ScenarioPage, step_result: StepResult):
        """
        Accès à l'application AAI2 depuis le portail.
        
        Navigation depuis le portail vers l'application métier AAI2.
        """
        # Localisation et clic sur lien AAI2
        aai2_link = page.get_by_role("link", name="AAI2")
        expect(aai2_link).to_be_visible(timeout=30000)
        
        page.screenshot("portail_avant_clic_aai2")
        aai2_link.click()
        
        # SUCCESS automatique si pas d'exception

    def test_accueil_aai2(self, page: ScenarioPage, step_result: StepResult):
        """
        Navigation dans l'accueil AAI2 vers la consultation des demandes.
        
        Utilise les iframes pour accéder aux fonctionnalités de l'application.
        """
        # Accès à l'iframe principale de l'application
        iframe_principale = page.frame_locator('iframe[name="iframe_principale"]')
        
        # Clic sur menu Demandes
        menu_demandes = iframe_principale.get_by_text("Demandes", exact=True)
        expect(menu_demandes).to_be_visible(timeout=30000)
        menu_demandes.click()
        
        # Clic sur sous-menu "Consulter une demande"
        lien_consulter = iframe_principale.get_by_role("link", name="Consulter une demande")
        expect(lien_consulter).to_be_visible(timeout=30000)
        
        page.screenshot("aai2_avant_clic_consulter")
        lien_consulter.click()

    def test_liste_demandes(self, page: ScenarioPage, step_result: StepResult):
        """
        Recherche d'une demande par nom.
        
        Saisie des critères de recherche et lancement de la recherche.
        """
        iframe_principale = page.frame_locator('iframe[name="iframe_principale"]')
        
        # Saisie du nom à rechercher
        champ_nom = iframe_principale.get_by_role("textbox", name="Nom")
        champ_nom.fill("test")
        
        # Clic sur bouton rechercher
        bouton_rechercher = iframe_principale.get_by_role("button", name="Rechercher")
        expect(bouton_rechercher).to_be_visible(timeout=30000)
        
        page.screenshot("recherche_avant_execution")
        bouton_rechercher.click()

    def test_resultat_recherche(self, page: ScenarioPage, step_result: StepResult):
        """
        Sélection d'une demande dans les résultats de recherche.
        
        Accès au détail d'une demande depuis la liste des résultats.
        """
        iframe_principale = page.frame_locator('iframe[name="iframe_principale"]')
        
        # Clic sur lien de visualisation de la demande
        lien_visualisation = iframe_principale.get_by_role("link", name="Visualisation de la demande")
        expect(lien_visualisation).to_be_visible(timeout=30000)
        
        page.screenshot("resultats_avant_selection")
        lien_visualisation.click()

    def test_detail_demande(self, page: ScenarioPage, step_result: StepResult):
        """
        Vérification de l'affichage du détail de la demande.
        
        Contrôle que la page de détail s'affiche correctement avec les informations.
        """
        iframe_principale = page.frame_locator('iframe[name="iframe_principale"]')
        
        # Vérification de la présence du titre de la page de détail
        titre_detail = iframe_principale.get_by_role("heading", name="Détail de la demande")
        expect(titre_detail).to_be_visible(timeout=30000)
        
        page.screenshot("detail_demande_affiche")

    def test_retour_portail_applicatif(self, page: ScenarioPage, step_result: StepResult):
        """
        Retour au portail applicatif depuis AAI2.
        
        Navigation de retour vers la page d'accueil du portail.
        """
        # Clic sur lien de retour (en dehors de l'iframe)
        lien_retour = page.get_by_role("link", name="Retour vers la page d'accueil")
        expect(lien_retour).to_be_visible(timeout=30000)
        lien_retour.click()
        
        # Vérification du retour sur le portail
        titre_portail = page.get_by_role("heading", name="Mes applications")
        expect(titre_portail).to_be_visible(timeout=30000)
        
        page.screenshot("retour_portail_confirme")
