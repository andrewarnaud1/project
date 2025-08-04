"""Fichier de gestion des erreurs timeouts."""

import logging
import re
from typing import List, Optional, Dict
from playwright.sync_api import Page
from src.utils.yaml_loader import load_yaml_file

LOGGER = logging.getLogger(__name__)


class VerificateurTimeout:
    """
    En cas de Timeout charge les fichiers d'erreurs et
    vérfie si ces erreurs sont présentent dans la page HTML.
    """

    def __init__(self, config_execution: Dict):
        self.config_execution = config_execution
        self.patterns = self._charger_fichiers_erreurs()
        self.patterns_charges = self.patterns is not None

    def _charger_fichiers_erreurs(self) -> Optional[Dict]:
        """Charge toutes les erreurs depuis les fichiers spécifiés et le fichier commun."""
        patterns_combines = {}
        fichiers_charges = []

        # Charger le fichier commun
        fichier_erreurs_commun = self._charger_fichier_commun()
        if fichier_erreurs_commun:
            patterns_combines = self._fusionner_fichiers_erreurs(
                patterns_combines, fichier_erreurs_commun
            )
            fichiers_charges.append("erreurs.yaml (commun)")
            LOGGER.info("[VerificateurTimeout] Fichier commun chargé")
        else:
            LOGGER.warning(
                "[VerificateurTimeout] Fichier commun introuvable - Aucune détection d'erreur"
            )
            return None

        # Charger les fichiers de scénarios
        fichiers_specifiques = self._charger_fichier_erreurs_scenario()
        if fichiers_specifiques:
            for nom_fichier in fichiers_specifiques:
                patterns_specifiques = self._charger_fichier_specifique(nom_fichier)
                if patterns_specifiques:
                    patterns_combines = self._fusionner_fichiers_erreurs(
                        patterns_combines, patterns_specifiques
                    )
                    fichiers_charges.append(f"{nom_fichier}.yaml")
                    LOGGER.info(
                        "[VerificateurTimeout] Fichier spécifique %s chargé",
                        nom_fichier,
                    )
                else:
                    LOGGER.warning(
                        "[VerificateurTimeout] Fichier spécifique %s introuvable",
                        nom_fichier,
                    )

        # Afficher un résumé des fichiers chargés
        if fichiers_charges:
            LOGGER.info(
                "[VerificateurTimeout] Fichiers chargés: %s",
                ", ".join(fichiers_charges),
            )

        return patterns_combines

    def _charger_fichier_commun(self) -> Optional[Dict]:
        """Charge le fichier de patterns commun"""
        try:
            scenarios_path = self.config_execution.get(
                "scenarios_path", "/opt/scenarios_v6"
            )
            chemin_fichier_commun = f"{scenarios_path}/erreurs/erreurs.yaml"

            return load_yaml_file(chemin_fichier_commun)
        except Exception as e:
            LOGGER.debug(
                "[VerificateurTimeout] Erreur chargement fichier commun : %s", e
            )
            return None

    def _charger_fichier_erreurs_scenario(self) -> List[str]:
        """Récupère la liste des fichiers spécifiques depuis la configuration"""
        # Chercher dans la configuration sous la clé 'fichiers_patterns_erreurs'
        fichiers_specifiques = self.config_execution.get("fichiers_erreurs", [])

        # S'assurer que c'est une liste
        if isinstance(fichiers_specifiques, str):
            fichiers_specifiques = [fichiers_specifiques]
        elif not isinstance(fichiers_specifiques, list):
            fichiers_specifiques = []

        LOGGER.debug(
            "[VerificateurTimeout] Fichiers spécifiques configurés : %s",
            fichiers_specifiques,
        )

        return fichiers_specifiques

    def _charger_fichier_specifique(self, nom_fichier: str) -> Optional[Dict]:
        """Charge un fichier de patterns spécifique"""
        try:
            scenarios_path = self.config_execution.get(
                "scenarios_path", "/opt/scenarios_v6"
            )

            # Ajouter l'extension .yaml si pas présente
            if not nom_fichier.endswith(".yaml"):
                nom_fichier = f"{nom_fichier}.yaml"

            chemin_fichier = f"{scenarios_path}/config/{nom_fichier}"

            return load_yaml_file(chemin_fichier)
        except Exception as e:
            LOGGER.debug(
                "[VerificateurTimeout] Erreur chargement fichier %s : %s",
                nom_fichier,
                e,
            )
            return None

    def _fusionner_fichiers_erreurs(
        self, patterns_base: Dict, nouveaux_patterns: Dict
    ) -> Dict:
        """Fusionne deux dictionnaires de patterns"""
        if not patterns_base:
            return nouveaux_patterns.copy()

        return patterns_base | nouveaux_patterns

    def verifier_cause_timeout(self, page: Page) -> Optional[str]:
        """
        Vérifie si un timeout est causé par une erreur visible dans la page

        Returns:
            str: Message d'erreur trouvé ou None si pas d'erreur ou pas de patterns
        """
        # Si aucun pattern n'est chargé, ne pas faire de recherche
        if not self.patterns_charges:
            LOGGER.debug(
                "[VerificateurTimeout] Aucun pattern chargé - Pas de vérification d'erreur"
            )
            return None

        try:
            # Chercher dans la page principale
            erreurs = self._chercher_erreurs_dans_page(page)

            # Chercher dans toutes les frames
            for frame in page.frames:
                if frame != page.main_frame:
                    try:
                        erreurs_frame = self._chercher_erreurs_dans_page(frame)
                        erreurs.extend(erreurs_frame)
                    except Exception as e:
                        LOGGER.debug(
                            "[VerificateurTimeout] Erreur frame %s : %s", frame.url, e
                        )

            # Retourner la première erreur trouvée
            if erreurs:
                return erreurs[0]

            return None

        except Exception as e:
            LOGGER.debug("[VerificateurTimeout] Erreur vérification : %s", e)
            return None

    def _chercher_erreurs_dans_page(self, page_ou_frame) -> List[str]:
        """Cherche les erreurs dans une page ou frame"""
        erreurs = []

        try:
            # Récupérer le contenu HTML
            contenu_html = page_ou_frame.content()

            # Chercher les codes d'erreur spécifiques
            erreurs_codes = self._chercher_codes_erreur(contenu_html)
            erreurs.extend(erreurs_codes)

            # Si pas de code trouvé, chercher les messages génériques
            if not erreurs_codes:
                erreurs_messages = self._chercher_messages_erreur(contenu_html)
                erreurs.extend(erreurs_messages)

            # Chercher dans les éléments visibles
            erreurs_elements = self._chercher_dans_elements(page_ou_frame)
            erreurs.extend(erreurs_elements)

        except Exception as e:
            LOGGER.debug("[VerificateurTimeout] Erreur recherche: %s", e)

        return erreurs[:2]  # Limiter à 2 erreurs

    def _chercher_codes_erreur(self, contenu_html: str) -> List[str]:
        """Cherche les codes d'erreur HTTP dans le HTML"""
        erreurs = []
        html_minuscule = contenu_html.lower()

        patterns_codes = self.patterns.get("detection_erreurs", {}).get(
            "codes_http", []
        )

        for pattern in patterns_codes:
            matches = re.finditer(pattern, html_minuscule, re.IGNORECASE)
            for match in matches:
                if match.groups():
                    code_erreur = int(match.group(1))
                    message_formate = self._formater_message_erreur(code_erreur)
                    erreurs.append(message_formate)

                    # Limiter à 2 codes
                    if len(erreurs) >= 2:
                        return erreurs

        return erreurs

    def _chercher_messages_erreur(self, contenu_html: str) -> List[str]:
        """Cherche les messages d'erreur génériques de tous types"""
        erreurs = []
        html_minuscule = contenu_html.lower()

        messages_erreur = self.patterns.get("detection_erreurs", {}).get(
            "messages_erreur", {}
        )

        for type_erreur, patterns in messages_erreur.items():
            for pattern in patterns:
                if re.search(pattern, html_minuscule, re.IGNORECASE):
                    description_type = self._get_description_type(type_erreur)
                    if type_erreur in ["4xx", "5xx"]:
                        # Erreurs HTTP
                        erreurs.append(f"{description_type} ({type_erreur}) détectée")
                    else:
                        # Autres types d'erreur
                        erreurs.append(f"{description_type} détectée")
                    return erreurs

        return erreurs

    def _chercher_dans_elements(self, page_ou_frame) -> List[str]:
        """Cherche dans les éléments visibles"""
        erreurs = []

        selecteurs = self.patterns.get("detection_erreurs", {}).get("selecteurs", [])

        for selecteur in selecteurs:
            try:
                elements = page_ou_frame.locator(selecteur).all()

                for element in elements:
                    try:
                        texte = element.inner_text(timeout=500).strip()
                        if texte:
                            # Chercher un code d'erreur dans le texte
                            codes_trouves = re.findall(r"([45]\d{2})", texte)
                            if codes_trouves:
                                code_erreur = int(codes_trouves[0])
                                message_formate = self._formater_message_erreur(
                                    code_erreur
                                )
                                erreurs.append(message_formate)
                                return erreurs
                    except Exception as e:
                        LOGGER.debug(
                            "[VerificateurTimeout] Erreur lecture texte élément %s : %s",
                            selecteur,
                            e,
                        )

            except Exception as e:
                LOGGER.debug(
                    "[VerificateurTimeout] Erreur sélecteur %s : %s", selecteur, e
                )

        return erreurs

    def _formater_message_erreur(self, code_erreur: int) -> str:
        """Formate un message d'erreur avec le type d'erreur."""
        type_erreur = self._get_type_erreur(code_erreur)
        description_type = self._get_description_type(type_erreur)
        description_code = self._get_description_code(code_erreur)

        return f"{description_type} ({type_erreur}) - {code_erreur} {description_code}"

    def _get_type_erreur(self, code_erreur: int) -> str:
        """Détermine le type d'erreur (4xx, 5xx, etc.)"""
        if 400 <= code_erreur <= 499:
            return "4xx"
        elif 500 <= code_erreur <= 599:
            return "5xx"
        elif 300 <= code_erreur <= 399:
            return "3xx"
        else:
            return "autre"

    def _get_description_type(self, type_erreur: str) -> str:
        """Récupère la description d'un type d'erreur"""
        descriptions = self.patterns.get("descriptions_types", {})
        return descriptions.get(type_erreur, "Erreur inconnue")

    def _get_description_code(self, code_erreur: int) -> str:
        """Récupère la description d'un code d'erreur"""
        descriptions = self.patterns.get("descriptions_codes", {})
        return descriptions.get(code_erreur, f"Code {code_erreur}")
