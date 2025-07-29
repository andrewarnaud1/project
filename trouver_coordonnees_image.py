"""Ce module permets de comparer deux images entre elles."""

import cv2


def trouver_coordonnees_image(
    template_path,
    screenshot_path="scenarios_exadata/img/screenshot_ecran.png",
):
    """
    Permets de comparer deux images.

    Args:
        template_path:
        screenshot_path:
    """

    # Lecture du screenshot
    screenshot = cv2.imread(screenshot_path)

    # Lecture de l'image à trouver à l'écran
    template = cv2.imread(template_path)

    # Recherche de l'image à trouver dans le screenshot de l'écran actuel
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

    # Intervalle de confiance
    confiance = 0.8

    # Localisation des coordonnées du coin haut droit de l'image
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Vérifier si l'image est trouvée avec une confiance dans l'intervalle
    if max_val >= confiance:
        coords = []

        # Récupération de la taille de l'image
        height, width, channels = template.shape

        # Calcul des coordonnées du centre de l'image
        center_x = max_loc[0] + (width / 2)
        center_y = max_loc[1] + (height / 2)

        # Ajout des coordonnées du centre de l'image
        coords.append(center_x)
        coords.append(center_y)

        print(f"Coordonnées de l'image ({template_path}) trouvées avec une confiance de {max_val}")
        return coords
    else:
        print("Coordonnées de l'image non trouvées")
        return None
