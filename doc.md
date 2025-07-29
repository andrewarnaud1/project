# Documentation scénario exadata


- Guacamole
- Windows 11
- Firefox (à voir pour l'implémentation avec Edge)



Playwright est un framework d'automatisation des tests de bout en bout basé uniquement pour réaliser des actions WEB. Cependant, les scénarios exadata nécessite d'intérargir avec des applications directement dans Windows.
Ainsi pour réussir à ouvrir la VM on utilise Guacamole (expliquer à quoi sert Guacamole) et on se connecte avec Playwright.
Pour qu'un scénario exadata fonctionne il faut prendre des screenshots de chaque objet sur lequel on souhaite cliquer (expliquer qu'il faut la même résolution qui sera ouvert par Playwreight lors du déroulement du scénario).
On prends des screenshot continuel de la page et à chaque fois on vérifie que que l'élement que 'on cherche se trouver sur le screenshot. Si c'est le cas on localise les coordonnées.
On transmets les coordonnées à Playwright pour qu'il click à l'endroit voulu.



Utilisation cv2 de Python pour localiser la comparaison d'images.
Configuration de Firefox.




Avant de lancer le scénario en V6 il faut s'assurer que :

1. Firefox n'enregistre pas les les identifiants de connexion
2. Firefox lance automatiquement les fichier '.jnlp' après le téléchargement
