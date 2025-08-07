# ==========================================

# MODIFICATION 1 : etape.py

# ==========================================

“”“Gestion des Etapes d’un scenario”””

import time
from datetime import datetime
import logging
import inspect
import pytest
from playwright.sync_api import sync_playwright

from src.utils.utils import contexte_actuel

LOGGER = logging.getLogger(**name**)

class Etape:
“”“Gestion des étapes d’une execution (instance de test de scenario)”””

```
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
    
    # NOUVEAU : Compteur de screenshot pour cette étape
    self.compteur_screenshot = 0
    
    LOGGER.debug(
        "[%s] etape créée => %s", inspect.currentframe().f_code.co_name, self.etape
    )

def __str__(self):
    return f"{self.etape}"

def incrementer_screenshot(self):
    """
    Incrémente le compteur de screenshot et retourne le numéro actuel.
    
    Returns:
        int: Numéro du screenshot dans cette étape (commence à 1)
    """
    self.compteur_screenshot += 1
    LOGGER.debug(
        "[Etape.incrementer_screenshot] Screenshot #%d pour l'étape '%s'", 
        self.compteur_screenshot, 
        self.etape['nom']
    )
    return self.compteur_screenshot

def get_compteur_screenshot(self):
    """
    Retourne le nombre actuel de screenshots pris dans cette étape.
    
    Returns:
        int: Nombre de screenshots pris
    """
    return self.compteur_screenshot

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
    
    # NOUVEAU : Log du nombre de screenshots pris
    if self.compteur_screenshot > 0:
        LOGGER.info(
            "[Etape.finalise] Étape '%s' terminée avec %d screenshot(s)", 
            self.etape['nom'], 
            self.compteur_screenshot
        )
    
    if self.etape["status"] == 0:
        LOGGER.info("✅ %s", commentaire)
    elif self.etape["status"] == 1:
        LOGGER.warning("⚠️ %s", commentaire)
    else:
        LOGGER.error("❌ %s", commentaire)
    LOGGER.info("Etape [%s] ----  FIN  ----", self.etape["nom"])
```

@pytest.fixture(scope=“function”)
def etape(execution, request):
“””
Pemret de générer la page à partir du contexte
“””
fixture_name = inspect.currentframe().f_code.co_name
LOGGER.debug(”[Fixture SETUP %s] ––  DEBUT  ––”, fixture_name)
etape = Etape(request)
execution.compteur_etape += 1
LOGGER.debug(”[Fixture SETUP %s] ––   FIN  ––”, fixture_name)

```
yield etape

LOGGER.debug("[Fixture FINAL %s] ----  DEBUT ----", fixture_name)

# NOUVEAU : Log détaillé du nombre de screenshots
LOGGER.info(
    "[Fixture FINAL %s] Étape %d '%s' : %d screenshot(s) pris", 
    fixture_name,
    execution.compteur_etape,
    etape.etape['nom'],
    etape.compteur_screenshot
)

execution.ajoute_etape(etape.etape)
LOGGER.debug(
    "[Fixture FINAL %s] (%s)etapes => %s ",
    fixture_name,
    type(execution.etapes),
    execution.etapes,
)
LOGGER.debug("[Fixture FINAL %s] ----   FIN  ----", fixture_name)
```

# ==========================================

# MODIFICATION 2 : screenshot_manager.py

# ==========================================

import logging
from datetime import datetime
from src.utils.utils import contexte_actuel

LOGGER = logging.getLogger(**name**)

def take_screenshot(
execution, etape, page, erreur=False, curseur_element=None, elts_flous=None, decoration=True
):
“””
Prend une capture d’écran de la page et l’annotée directement via HTML/CSS.

```
Args:
    execution: L'objet Execution pour gérer les chemins des captures d'écran
    etape: L'objet Etape pour gérer les annotations
    page: L'objet Page de Playwright
    erreur: L'erreur à annoter sur la capture d'écran (booleen)
    curseur_element: Element sur lequel dessiner le curseur
    elts_flous : elements à flouter
    decoration: Ajouter les décorations (bannière, curseur)

Returns:
    str: Chemin relatif vers la capture d'écran
"""
methode_name = contexte_actuel()
LOGGER.debug("[%s] ---- DEBUT ----", methode_name)
start = datetime.now()
LOGGER.debug("[%s] curseur_element => %s", methode_name, curseur_element)

if execution.config["screenshot_dir"] is None:
    screenshot_path = None
    LOGGER.warning(
        "[%s]⚠️ Pas de répertoire de capture d'écran configuré", methode_name
    )
else:
    # NOUVEAU : Utiliser le compteur de screenshot de l'étape
    numero_screenshot = etape.incrementer_screenshot()
    
    # Construction du nom de fichier avec le compteur
    if erreur:
        screenshot_basename = (
            f"{execution.compteur_etape:02d}_{numero_screenshot:02d}_Erreur_{etape.etape['nom']}"
        )
        screenshot_title = f"❗{screenshot_basename}"
    else:
        screenshot_basename = (
            f"{execution.compteur_etape:02d}_{numero_screenshot:02d}_{etape.etape['nom']}"
        )
        screenshot_title = f"✅{screenshot_basename}"
        
    screenshot_path = (
        f"{execution.config['screenshot_dir']}/{screenshot_basename}.png"
    )
    
    LOGGER.info(
        "[%s] Prise du screenshot #%d pour l'étape %d : %s", 
        methode_name, 
        numero_screenshot,
        execution.compteur_etape,
        screenshot_basename
    )

    if decoration:
        original_border = decoration_avant_screenshot(
            page, screenshot_title, curseur_element, elts_flous=elts_flous
        )
    else:
        original_border = None

    # Prendre la capture d'écran
    try:
        page.screenshot(
            path=str(screenshot_path), full_page=True
        )
        LOGGER.debug("[%s] Screenshot sauvegardé : %s", methode_name, screenshot_path)
    except Exception as exception:
        LOGGER.warning(
            "[%s]⚠️ Erreur de capture d'écran : %s", methode_name, exception
        )

    # Suppression la bannière et des décorations
    if decoration:
        try:
            page.evaluate(
                "() => { const el = document.getElementById('screenshot-banner'); if (el) el.remove(); }"
            )
        except Exception as e:
            LOGGER.warning(
                "[%s]⚠️ Echec de suppression de la bannière de capture d'écran : %s",
                methode_name,
                e,
            )

        # Suppression de la bordure et du curseur
        if curseur_element is not None:
            if "original_border" in locals() and original_border is not None:
                curseur_element.evaluate(
                    "(el, original) => el.style.border = original", original_border
                )
            page.evaluate(
                "() => { const el = document.getElementById('screenshot-mouse-pointer'); if (el) el.remove(); }"
            )

duree_ms = (int)((datetime.now() - start).total_seconds() * 1000)
LOGGER.debug("[%s]⏱️ ----  FIN  ---- (durée : %.2f ms)", methode_name, duree_ms)
return str(screenshot_path)
```

def get_screenshot_info(etape):
“””
Retourne des informations sur les screenshots de l’étape.

```
Args:
    etape: L'objet Etape
    
Returns:
    dict: Informations sur les screenshots
"""
return {
    "nom_etape": etape.etape['nom'],
    "nombre_screenshots": etape.compteur_screenshot,
    "prochain_numero": etape.compteur_screenshot + 1
}
```

# NOUVEAU : Fonction utilitaire pour decorator_avant_screenshot (pas de changement)

def decoration_avant_screenshot(page, titre_page, curseur_element=None, elts_flous=[]):
“””
Ajout des décorations (banières, pointeur de souris, floutage des éléments)
Important : Il faut rajouter la banière en dernier pour garder la resolution xpath

```
Args:
    page: L'objet Page de Playwright
    page_title: Titre de la page ou identifiant pour le nom du fichier
    screen_shot_number : Numero de screnshot
    curseur_element: Element sur lequel dessiner le curseur
    elts_flous : elements à flouter
"""
methode_name = contexte_actuel()
LOGGER.debug("[%s] ---- DEBUT ----", methode_name)
LOGGER.debug("[%s] curseur_element => %s", methode_name, curseur_element)

if elts_flous is not None:
    for elt in elts_flous:
        LOGGER.debug("[%s] element à flouter => %s", methode_name, elt)
        elt.evaluate(
            "element => element.style.setProperty('filter', 'blur(2px)' , 'important')"
        )

if curseur_element is not None:
    try:
        original_border = curseur_element.evaluate(
            "el => getComputedStyle(el).border"
        )
        curseur_element.evaluate(
            "element => element.style.setProperty('border', '2px solid green')"
        )

        # Calcul de la position du curseur (centre de l'element)
        box = curseur_element.bounding_box()
        posx = (int)(box["x"] + box["width"] / 2)
        posy = (int)(box["y"] + 30 + box["height"] / 2)
        LOGGER.debug(
            f"[decoration_avant_screenshot] box => {box}, posx => {posx}, posy => {posy}"
        )
    except Exception as exception:
        LOGGER.warning(
            "[%s]⚠️ Echec du calcul de la position du curseur : %s",
            methode_name,
            exception,
        )
    else:
        # Injection du pointeur (en javascript) dans la page
        script = f"""
            const existing = document.getElementById('screenshot-mouse-pointer');
            if (existing) existing.remove();

            const pointer = document.createElement('div');
            pointer.id = 'screenshot-mouse-pointer';
            pointer.style.cssText = `
                position: absolute;
                z-index: 9999999;
                width: 20px;
                height: 30px;
                background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAeCAQAAACGG/bgAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAHsYAAB7GAZEt8iwAAAAHdElNRQfgAwgMIwdxU/i7AAABZklEQVQ4y43TsU4UURSH8W+XmYwkS2I09CRKpKGhsvIJjG9giQmliHFZlkUIGnEF7KTiCagpsYHWhoTQaiUUxLixYZb5KAAZZhbunu7O/PKfe+fcA+/pqwb4DuximEqXhT4iI8dMpBWEsWsuGYdpZFttiLSSgTvhZ1W/SvfO1CvYdV1kPghV68a30zzUWZH5pBqEui7dnqlFmLoq0gxC1XfGZdoLal2kea8ahLoqKXNAJQBT2yJzwUTVt0bS6ANqy1gaVCEq/oVTtjji4hQVhhnlYBH4WIJV9vlkXLm+10R8oJb79Jl1j9UdazJRGpkrmNkSF9SOz2T71s7MSIfD2lmmfjGSRz3hK8l4w1P+bah/HJLN0sys2JSMZQB+jKo6KSc8vLlLn5ikzF4268Wg2+pPOWW6ONcpr3PrXy9VfS473M/D7H+TLmrqsXtOGctvxvMv2oVNP+Av0uHbzbxyJaywyUjx8TlnPY2YxqkDdAAAAABJRU5ErkJggg==');
                background-repeat: no-repeat;
                background-size: contain;
                pointer-events: none;
                left: {posx}px;
                top: {posy}px;
            `;
            document.body.appendChild(pointer);
            """
        try:
            page.evaluate(script)
        except Exception as exception:
            LOGGER.warning(
                "[%s]⚠️ Echec d'injection du curseur : %s", methode_name, exception
            )
    return original_border

annotation_text = (
    f"{titre_page} - ({page.url}) - {datetime.now().strftime('%H:%M:%S')}"
)
try:
    page.evaluate(
        f"""
        () => {{
            const existing = document.getElementById('screenshot-banner');
            if (existing) existing.remove();

            let banner = document.createElement('div');
            banner.id = 'screenshot-banner';
            banner.textContent = `{annotation_text}`;
            Object.assign(banner.style, {{
                top: '0px',
                left: '0px',
                right: '0px',
                background: 'white',
                color: 'black',
                fontSize: '12px',
                padding: '4px 10px',
                borderBottom: '1px solid #ccc',
                zIndex: 99999,
                fontFamily: 'monospace',
                textAlign: 'left',
                display: 'block',
                alignItems: 'center'
            }});
            document.body.prepend(banner);
        }}
    """
    )
except Exception as exception:
    LOGGER.warning(
        "[%s]⚠️ Echec de création de la bannière de capture d'écran : %s",
        methode_name,
        exception,
    )
```