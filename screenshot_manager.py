import logging

from datetime import datetime

from src.utils.utils import contexte_actuel

LOGGER = logging.getLogger(__name__)


def decoration_avant_screenshot(page, titre_page, curseur_element=None, elts_flous=[]):
    """
    Ajout des décorations (banières, pointeur de souris, floutage des éléments)
    Important : Il faut rajouter la banière en dernier pour garder la resolution xpath

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
            # TODO : Mettre seulement en développement de scénario (ajouter une varible d'environnement et faire une condition)
            original_border = curseur_element.evaluate(
                "el => getComputedStyle(el).border"
            )
            curseur_element.evaluate(
                "element => element.style.setProperty('border', '2px solid green')"
            )
            # curseur_element.evaluate("element => element.style.setProperty('border', '10px solid red')")

            # Calcul de la position du curseur (centre de l'element)
            # box = curseur_element.with_timeout(0).bounding_box()
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
            # # javascript d'injection du curseur (flèche en base64) Version pointeur rouge
            # script = f"""
            #     const existing = document.getElementById('screenshot-mouse-pointer');
            #     if (existing) existing.remove();

            #     const pointer = document.createElement('div');
            #     pointer.id = 'screenshot-mouse-pointer';
            #     pointer.style.cssText = `
            #         position: absolute;
            #         z-index: 9999999;
            #         width: 16px;
            #         height: 16px;
            #         background: red;
            #         border-radius: 50%;
            #         left: {posx}px;
            #         top: {posy}px;
            #         pointer-events: none;
            #     `;
            #     document.body.appendChild(pointer);
            #     """

            # Injection du pointeur (en javascript) dans la pageop
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


def take_screenshot(
    execution, etape, page, erreur=False, curseur_element=None, elts_flous=None, decoration=True
):
    """
    Prend une capture d'écran de la page et l'annotée directement via HTML/CSS.

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
        # TODO Andrew : HIDE ELEMENTS WHEN SCREENSHOTING (https://github.com/microsoft/playwright/issues/10162)

        # Le nom du fichier de capture d'écran est prefixé par "Erreur" si erreur
        if erreur:
            screenshot_basename = (
                f"{execution.compteur_etape:02d}_Erreur_{etape.etape['nom']}"
            )
            screenshot_title = f"❗{screenshot_basename}"
        else:
            screenshot_basename = f"{execution.compteur_etape:02d}_{etape.etape['nom']}"
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
            # TODO Andrew : Choisir la couleur pour masker des éléments
            page.screenshot(
                path=str(screenshot_path), full_page=True
            )  # , mask=elts_flous)
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
