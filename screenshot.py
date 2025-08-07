# Modification dans etape.py

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
    # AJOUT : Compteur de screenshot pour cette étape
    self.compteur_screenshot = 0
    LOGGER.debug(
        "[%s] etape créée => %s", inspect.currentframe().f_code.co_name, self.etape
    )

def incrementer_screenshot(self):
    """Incrémente le compteur de screenshot et retourne la valeur"""
    self.compteur_screenshot += 1
    return self.compteur_screenshot
```

# Modification dans screenshot_manager.py

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
    # MODIFICATION : Utiliser le compteur de screenshot de l'étape
    numero_screenshot = etape.incrementer_screenshot()
    
    # Le nom du fichier inclut maintenant le numéro de screenshot dans l'étape
    if erreur:
        screenshot_basename = (
            f"{execution.compteur_etape:02d}_{numero_screenshot:02d}_Erreur_{etape.etape['nom']}"
        )
        screenshot_title = f"❗{screenshot_basename}"
    else:
        screenshot_basename = f"{execution.compteur_etape:02d}_{numero_screenshot:02d}_{etape.etape['nom']}"
        screenshot_title = f"✅{screenshot_basename}"
        
    screenshot_path = (
        f"{execution.config['screenshot_dir']}/{screenshot_basename}.png"
    )
    LOGGER.debug("[%s] screenshot_path => %s", methode_name, screenshot_path)

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
    except Exception as exception:
        LOGGER.warning(
            "[%s]⚠️ Erreur de capture d'écran : %s", methode_name, exception
        )

    # Suppression la bannière
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