"""
Ce module vise à boucler sur des données de test, telles que «nom d'utilisateur et mot de passe»,
pour les utiliser dans un scénario à chaque répétition itérative du scénario.
C'est comme si, la première fois, j'utilisais le premier utilisateur et le premier mot de passe.
Puis que la deuxième fois, j'exécutais le même scénario avec un nouvel utilisateur et un
nouveau mot de passe, et ainsi de suite.
"""

import os


def read_cache_file(chemin_fichier_texte):
    """
    retourne l'indice actuel du fichier cache
    """

    # Vérifier si le répertoire cache existe, sinon le créer
    os.makedirs(os.path.dirname(chemin_fichier_texte), exist_ok=True)

    # Si le fichier n'existe pas, le créer avec la valeur 0
    if not os.path.exists(chemin_fichier_texte):
        with open(chemin_fichier_texte, "w", encoding="UTF-8") as text_file:
            text_file.write("0")
        return 0

    # Si le fichier existe, lire sa valeur
    with open(chemin_fichier_texte, "r", encoding="UTF-8") as text_file:
        file_content = text_file.read().strip()
        try:
            return int(file_content)
        except ValueError:
            # En cas d'erreur de conversion, réinitialiser à 0
            return 0


def write_cache_file(chemin_fichier_texte, value):
    """
    Écrit une nouvelle valeur dans le fichier cache
    """
    with open(chemin_fichier_texte, "w", encoding="UTF-8") as text_file:
        text_file.write(str(value))


def get_conf_data_from_scenario(cle, config):
    """
    Rotation sur les valeurs du tableau datas
    """

    chemin_fichier_texte = f"{config.get('output_path')}/cache{f'{config.get('nom_application')}/' if 'nom_application' in config.keys() else ''}/{config.get('nom_scenario')}.txt"

    print(f"Vérifier si vrai : {cle} {cle in config.keys()}")

    if f"{cle}" in config.keys():
        datas = config.get(cle)

        # taille du tableau
        list_size = len(datas)

        if list_size == 0:
            raise ValueError(
                f"Aucune donnée trouvée dans les données transmises : '{datas}'"
            )

        # Lire l'indice actuel
        current_index = read_cache_file(chemin_fichier_texte)

        # Vérifier si l'indice est valide
        if current_index >= list_size:
            current_index = 0

        # Récupérer l'élément correspondant à l'indice
        current_element = datas[current_index]

        # Incrémenter l'indice et sauvegarder
        next_index = current_index + 1
        write_cache_file(chemin_fichier_texte, next_index)
    else:
        current_element = None

    return current_element
