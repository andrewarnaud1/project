import logging
from src.utils.utils import contexte_actuel
from .yaml_loader import load_yaml_file

from .decrypt import decryptage_utilisateur

LOGGER = logging.getLogger(__name__)


def recuperer_utlisateur_isac(configuration):
    '''
    Méthode de récupération des données du fichier d'agent fictif
    '''
    methode_name = contexte_actuel()
    LOGGER.debug('[%s] ---- DEBUT ----', methode_name)
    
    utilisateur_isac = {}
    
    # Création du chemin du fichier dans lequele se trouver l'utilisateur fictif
    chemin_fichier_agent_fictif = f'{configuration['path_utilisateurs_isac']}/{configuration['utilisateur_isac']}.conf'

    # Chargement des données depuis le fichier YAML
    donnees_fichier_utilisateur = load_yaml_file(chemin_fichier_agent_fictif)

    # Récupération des valeurs associé à la plateforme
    donnees_fichier_utilisateur = donnees_fichier_utilisateur[configuration['plateforme']]

    for cle in donnees_fichier_utilisateur.keys():
        valeur = donnees_fichier_utilisateur.get(f'{cle}')
        LOGGER.debug('[recuperer_utlisateur_isac] clé : %s | valeurs : %s | type valeur %s', cle, valeur, type(valeur))
        if isinstance(valeur, dict):
            if 'crypte' in valeur.keys() and valeur['crypte']:
                valeur_decrypte = decryptage_utilisateur(valeur['valeur'])
                utilisateur_isac[cle] = valeur_decrypte
            else:
                utilisateur_isac[cle] = valeur
        if isinstance(valeur, str):
            utilisateur_isac[cle] = valeur

    LOGGER.debug('[%s] ----  FIN  ----', methode_name)

    return utilisateur_isac