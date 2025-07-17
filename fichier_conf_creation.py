import pandas as pd
import os
import yaml
from pathlib import Path

def generer_fichiers_conf(fichier_excel, nom_colonne='nom_fichier', dossier_sortie='fichiers_conf'):
    """
    Génère des fichiers .conf à partir d'un fichier Excel
    
    Args:
        fichier_excel (str): Chemin vers le fichier Excel
        nom_colonne (str): Nom de la colonne contenant les noms de fichiers
        dossier_sortie (str): Dossier où créer les fichiers .conf
    """
    
    # Lire le fichier Excel
    try:
        df = pd.read_excel(fichier_excel)
        print(f"Fichier Excel lu avec succès. {len(df)} lignes trouvées.")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier Excel: {e}")
        return
    
    # Vérifier que la colonne existe
    if nom_colonne not in df.columns:
        print(f"Colonne '{nom_colonne}' non trouvée.")
        print(f"Colonnes disponibles: {list(df.columns)}")
        return
    
    # Créer le dossier de sortie s'il n'existe pas
    Path(dossier_sortie).mkdir(parents=True, exist_ok=True)
    
    # Traiter chaque ligne
    fichiers_crees = 0
    for index, row in df.iterrows():
        nom_fichier = row[nom_colonne]
        
        # Ignorer les valeurs vides ou NaN
        if pd.isna(nom_fichier) or nom_fichier == '':
            print(f"Ligne {index + 1}: nom de fichier vide, ignorée")
            continue
        
        # Nettoyer le nom du fichier (supprimer les caractères problématiques)
        nom_fichier = str(nom_fichier).strip()
        
        # Créer le contenu YAML
        contenu_yaml = {
            'prod': {
                'utilisateur': nom_fichier,
                'mot_de_passe': {
                    'valeur': {
                        'key_aes': '',
                        'iv_base64': '',
                        'data_base64': ''
                    },
                    'crypte': True
                }
            }
        }
        
        # Nom du fichier de sortie
        nom_fichier_conf = f"{nom_fichier}.conf"
        chemin_fichier = os.path.join(dossier_sortie, nom_fichier_conf)
        
        # Écrire le fichier
        try:
            with open(chemin_fichier, 'w', encoding='utf-8') as f:
                yaml.dump(contenu_yaml, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            print(f"Fichier créé: {chemin_fichier}")
            fichiers_crees += 1
            
        except Exception as e:
            print(f"Erreur lors de la création du fichier {nom_fichier_conf}: {e}")
    
    print(f"\nTerminé! {fichiers_crees} fichiers .conf créés dans le dossier '{dossier_sortie}'")

# Exemple d'utilisation
if __name__ == "__main__":
    # Remplacez par le chemin vers votre fichier Excel
    fichier_excel = "votre_fichier.xlsx"
    
    # Remplacez par le nom de votre colonne si différent
    nom_colonne = "nom_fichier"  # ou le nom réel de votre colonne
    
    # Appeler la fonction
    generer_fichiers_conf(fichier_excel, nom_colonne)
    
    # Alternativement, vous pouvez spécifier un dossier de sortie différent:
    # generer_fichiers_conf(fichier_excel, nom_colonne, "mon_dossier_conf")
