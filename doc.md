# Documentation complète - Framework d’automatisation Exadata

## Vue d’ensemble

Ce framework d’automatisation permet d’interagir avec des applications Windows via Guacamole en utilisant une approche hybride combinant Playwright pour le web et OpenCV pour la reconnaissance d’images. Il est spécialement conçu pour automatiser les scénarios Exadata.

## Architecture du système

### Stack technologique

- **Guacamole** : Interface web pour accéder à distance aux applications Windows
- **Windows 11** : Environnement d’exécution des applications cibles
- **Firefox** : Navigateur principal (Edge en cours d’implémentation)
- **Playwright** : Framework d’automatisation web pour contrôler le navigateur
- **OpenCV (cv2)** : Bibliothèque de vision par ordinateur pour la reconnaissance d’images

### Principe de fonctionnement

1. **Connexion** : Playwright se connecte à l’interface Guacamole via Firefox
1. **Capture d’écran** : Prise de screenshots continus de la page web (interface Guacamole)
1. **Reconnaissance** : Comparaison des éléments recherchés avec les captures d’écran via OpenCV
1. **Localisation** : Calcul des coordonnées exactes des éléments trouvés
1. **Action** : Exécution des actions (clic, saisie) via Playwright aux coordonnées déterminées

## Modules et fonctions

### 1. Module `trouver_coordonnees_image.py`

**Fonction principale** : `trouver_coordonnees_image(template_path, screenshot_path)`

**Rôle** : Compare une image template avec un screenshot pour localiser les coordonnées du centre de l’élément.

**Paramètres** :

- `template_path` (str) : Chemin vers l’image de l’élément à rechercher
- `screenshot_path` (str, optionnel) : Chemin du screenshot de référence

**Retour** :

- Liste `[x, y]` des coordonnées du centre si trouvé
- `None` si l’élément n’est pas trouvé

**Configuration** :

- Seuil de confiance : 0.8 (80% de correspondance minimum)
- Méthode de matching : `cv2.TM_CCOEFF_NORMED`

### 2. Module `verifier.py`

**Fonction principale** : `verifier(image_a_verifier, page, obligatoire, cpt_duree)`

**Rôle** : Vérifie la présence d’un élément sur la page avec un système de retry.

**Paramètres** :

- `image_a_verifier` (str) : Chemin de l’image à rechercher
- `page` (Page) : Instance Playwright de la page
- `obligatoire` (bool, défaut=True) : Lève une exception si non trouvé
- `cpt_duree` (int, défaut=150) : Nombre maximum de tentatives

**Retour** :

- Coordonnées `[x, y]` si trouvé
- `None` si non trouvé et non obligatoire
- Exception si non trouvé et obligatoire

**Comportement** :

- Attente active avec pause de 200ms entre les tentatives
- Screenshot automatique à chaque tentative

### 3. Module `cliquer.py`

**Fonction principale** : `cliquer(image_click, page, droit, obligatoire)`

**Rôle** : Effectue un clic sur un élément identifié par image.

**Paramètres** :

- `image_click` (str) : Chemin de l’image de l’élément à cliquer
- `page` (Page) : Instance Playwright
- `droit` (bool, défaut=False) : Clic droit si True, sinon clic gauche
- `obligatoire` (bool, défaut=True) : Comportement en cas d’échec

**Actions** :

- Localise l’élément via `verifier()`
- Exécute le clic aux coordonnées trouvées

### 4. Module `ecrire.py`

**Fonction principale** : `ecrire(image_champ_a_remplir, texte, page)`

**Rôle** : Saisit du texte dans un champ identifié par image.

**Paramètres** :

- `image_champ_a_remplir` (str) : Chemin de l’image du champ de saisie
- `texte` (str) : Texte à saisir
- `page` (Page) : Instance Playwright

**Comportement** :

- Clique sur le champ pour le sélectionner
- Saisit le texte caractère par caractère

## Guide d’utilisation

### Prérequis de configuration

#### Firefox

1. **Désactiver l’enregistrement des identifiants** :
- `about:config` → `signon.rememberSignons` → `false`
1. **Configuration automatique des fichiers JNLP** :
- Paramètres → Général → Applications
- Configurer `.jnlp` pour ouverture automatique

#### Capture d’images template

- **Résolution critique** : Les images template doivent être capturées à la même résolution que celle utilisée par Playwright
- **Format recommandé** : PNG pour préserver la qualité
- **Contenu** : Capturer uniquement l’élément ciblé, éviter les éléments variables (timestamps, compteurs)

### Exemple d’utilisation complète

```python
from playwright.sync_api import sync_playwright
from modules.cliquer import cliquer
from modules.ecrire import ecrire
from modules.verifier import verifier

def scenario_connexion():
    with sync_playwright() as p:
        # Lancement du navigateur
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        
        # Navigation vers Guacamole
        page.goto("https://votre-guacamole-url.com")
        
        # Connexion
        ecrire("images/champ_username.png", "mon_utilisateur", page)
        ecrire("images/champ_password.png", "mon_mot_de_passe", page)
        cliquer("images/bouton_connexion.png", page)
        
        # Vérification de la connexion
        coords = verifier("images/indicateur_connecte.png", page, obligatoire=False)
        
        if coords:
            print("Connexion réussie")
            # Continuer le scénario...
        else:
            print("Échec de la connexion")
        
        browser.close()

if __name__ == "__main__":
    scenario_connexion()
```

### Bonnes pratiques

#### Organisation des images

```
scenarios_exadata/
├── img/
│   ├── screenshot_ecran.png  # Screenshot temporaire
│   └── templates/
│       ├── boutons/
│       ├── champs/
│       └── indicateurs/
```

#### Gestion d’erreurs

```python
try:
    cliquer("images/bouton_critique.png", page)
except Exception as e:
    print(f"Erreur lors du clic : {e}")
    # Stratégie de récupération
```

#### Optimisation des performances

- Utiliser `obligatoire=False` pour les éléments optionnels
- Ajuster `cpt_duree` selon la complexité de l’interface
- Réutiliser les coordonnées trouvées quand possible

## Dépannage

### Problèmes courants

**Image non trouvée** :

- Vérifier la résolution d’écran
- Contrôler la qualité de l’image template
- Ajuster le seuil de confiance si nécessaire

**Performances lentes** :

- Réduire `cpt_duree` pour les éléments rapides
- Optimiser la taille des images template
- Utiliser des zones de recherche plus petites

**Clics imprécis** :

- Vérifier le calcul du centre dans `trouver_coordonnees_image`
- Contrôler les coordonnées retournées
- Tester avec des éléments plus grands

### Debugging

```python
# Activer les logs de debug
import logging
logging.basicConfig(level=logging.DEBUG)

# Sauvegarder les screenshots pour analyse
page.screenshot(path=f"debug/screenshot_{timestamp}.png")
```

## Évolutions futures

- Support d’Edge en plus de Firefox
- Amélioration de la précision de reconnaissance
- Interface de configuration graphique
- Support multi-résolutions automatique
- Cache intelligent des coordonnées