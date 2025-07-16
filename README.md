Ah parfait ! Vous voulez juste améliorer la qualité du commentaire dans le JSON en fonction du type d’erreur détecté. Voici une modification simple et ciblée de votre `gestion_exception.py` :

## Modification de `gestion_exception.py`

```python
'''Module de gestion des exceptions'''
import re
import logging
import pytest

from src.utils.utils import contexte_actuel
from src.utils.screenshot_manager import take_screenshot

LOGGER = logging.getLogger(__name__)

def gestion_exception(execution, etape, page, exception: Exception):
    '''Gestion des exceptions'''
    methode_name = contexte_actuel()
    LOGGER.debug('[%s] ---- DEBUT ----', methode_name)
    
    # Pour la première page, l'url est "about:blank" => url_initiale !
    if len(execution.etapes) == 0:
        url = execution.config.get('url_initiale')
    else:
        url = page.url

    # NOUVEAU: Diagnostic simple pour améliorer le commentaire
    type_erreur = diagnostiquer_type_erreur(page, exception)
    
    commentaire = construire_commentaire_ameliore(
        etape.etape['nom'], 
        execution, 
        url, 
        exception, 
        type_erreur
    )
    
    LOGGER.error(f"❌{commentaire}")
    etape.finalise(execution.compteur_etape, 2, url, commentaire)

    # screenshot et sortie
    take_screenshot(execution, etape, page, erreur=True)
    LOGGER.info('[%s] Appel de pytest.exit(2)', methode_name)
    pytest.exit(2)

def diagnostiquer_type_erreur(page, exception):
    '''Diagnostic simple pour déterminer le type d'erreur'''
    
    exception_str = str(exception).lower()
    
    # 1. Vérifier les erreurs de page/serveur
    if any(pattern in exception_str for pattern in [
        'net::err_', 'ns_error_', 'connection refused', 'timeout',
        'dns lookup failed', 'ssl error', 'certificate error',
        'navigation', 'page closed', 'context disposed'
    ]):
        return 'probleme_page'
    
    # 2. Vérifier les erreurs HTTP dans l'URL ou le contenu
    try:
        url = page.url
        if any(pattern in url.lower() for pattern in ['404', '500', '502', '503', 'error']):
            return 'erreur_http'
            
        title = page.title()
        if any(pattern in title.lower() for pattern in ['404', '500', 'error', 'not found', 'server error']):
            return 'erreur_http'
    except:
        pass
    
    # 3. Vérifier les erreurs de contenu de page
    try:
        body_text = page.locator('body').text_content(timeout=1000)
        if body_text and any(pattern in body_text.lower() for pattern in [
            '404 not found', '500 internal server error', 'access denied',
            'service unavailable', 'bad gateway'
        ]):
            return 'erreur_http'
    except:
        pass
    
    # 4. Par défaut, c'est un problème d'action
    return 'probleme_action'

def construire_commentaire_ameliore(nom_etape, execution, url, exception, type_erreur):
    '''Construction du commentaire amélioré selon le type d'erreur'''
    
    message_base = nettoyer_message(f"{exception}")
    
    if type_erreur == 'probleme_page':
        message = traduire_erreur_page(message_base, execution, url)
    elif type_erreur == 'erreur_http':
        message = traduire_erreur_http(message_base, execution, url)
    else:
        # Problème d'action - utiliser la traduction existante
        message = traduire_erreur(message_base, execution, url)
    
    commentaire = f"KO - Etape {execution.compteur_etape} {nom_etape} : {message}"
    return commentaire

def traduire_erreur_page(message, execution, url):
    '''Traduction spécifique pour les problèmes de page'''
    
    # Patterns spécifiques aux problèmes de page
    if 'connection refused' in message.lower():
        return f"Connexion refusée vers {url}"
    elif 'timeout' in message.lower():
        return f"Timeout lors de l'accès à {url}"
    elif 'dns lookup failed' in message.lower():
        return f"Résolution DNS échouée pour {url}"
    elif 'ssl error' in message.lower():
        return f"Erreur SSL sur {url}"
    elif 'navigation' in message.lower():
        return f"Erreur de navigation vers {url}"
    elif 'page closed' in message.lower():
        return "La page a été fermée de manière inattendue"
    elif 'context disposed' in message.lower():
        return "Le contexte de navigation a été fermé"
    
    # Traduction des erreurs réseau spécifiques
    ERRORS_RESEAU = {
        "NS_ERROR_PROXY_CONNECTION_REFUSED": f"Connexion au proxy refusée ({execution.config.get('proxy', 'N/A')})",
        "NS_ERROR_UNKNOWN_PROXY_HOST": f"Proxy introuvable ({execution.config.get('proxy', 'N/A')})",
        "NS_ERROR_CONNECTION_REFUSED": f"Serveur {url} refuse la connexion",
        "NS_ERROR_NET_TIMEOUT": f"Timeout réseau vers {url}",
        "NS_ERROR_UNKNOWN_HOST": f"Serveur {url} introuvable",
        "NS_ERROR_NET_RESET": f"Connexion interrompue vers {url}",
        "SSL_ERROR_UNKNOWN": f"Erreur SSL sur {url}"
    }
    
    for code, trad in ERRORS_RESEAU.items():
        if code in message:
            return trad
    
    return f"Problème de page sur {url} : {message}"

def traduire_erreur_http(message, execution, url):
    '''Traduction spécifique pour les erreurs HTTP'''
    
    if '404' in url or '404' in message:
        return f"Page non trouvée (404) : {url}"
    elif '500' in url or '500' in message:
        return f"Erreur serveur interne (500) : {url}"
    elif '502' in url or '502' in message:
        return f"Erreur de passerelle (502) : {url}"
    elif '503' in url or '503' in message:
        return f"Service indisponible (503) : {url}"
    
    return f"Erreur HTTP sur {url} : {message}"

# Garder les autres fonctions existantes inchangées
def construire_commentaire(nom_etape, execution, url, exception):
    '''Construction du commentaire (fonction existante conservée)'''
    message = nettoyer_message(f"{exception}")
    message = traduire_erreur(message, execution, url)
    
    commentaire = f"KO - Etape {execution.compteur_etape} {nom_etape} : {message}"
    return commentaire

# ... garder toutes les autres fonctions existantes (traduire_erreur, nettoyer_message, etc.)
```

## Résultat

Maintenant, vos commentaires dans le JSON seront beaucoup plus précis :

**Avant :**

```json
{
  "commentaire": "KO - Etape 3 connexion : Page.goto: NS_ERROR_CONNECTION_REFUSED"
}
```

**Après :**

```json
{
  "commentaire": "KO - Etape 3 connexion : Serveur https://example.com refuse la connexion"
}
```

**Ou pour une erreur 404 :**

```json
{
  "commentaire": "KO - Etape 5 validation : Page non trouvée (404) : https://example.com/missing-page"
}
```

Cette modification est **minimaliste** et **non-intrusive** - elle améliore simplement la qualité des commentaires d’erreur sans changer votre architecture existante.​​​​​​​​​​​​​​​​
