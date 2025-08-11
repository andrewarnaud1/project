Chaque test représente une étape.

Un scénario est composé d'une ou plusieurs étapes.
Une étape est composé d'une ou plusieurs actions.

Pour l'instant j'ai deux types de scénarios : exadata, web.
Les scénarios web sont des scénarios classiques pour lesquels on effectue des intéractions directement avec le navigateur.
Les scénario exadata sont des scénario qui sont des scénarios web mais leur objectif est de se rendre sur Guacamole, charger une VM et intérargir avec la VM pour tester des applications.
Pour les scénarios exadatas il faut quand même pouvoir réaliser des actions web puisque pour accèder à Guacamole cela se fait en Web.

Une étape peut être considérée comme ne faisant pas partie du scénario. Cela veut dire que cette étape ne doit pas être enregistrée. Ce type d'étape est enregistré seulement en cas d'erreur car cela permets d'indiquer qu'une erreur est survenue lors de l'execution du scénario mais que cette erreur n'est pas du au scénario en lui même mais à une étape d'initialisation comme l'ouverture du navigateur, le chargement d'une VM Guacamole, ...

Voici les pré-requis pour le lancement d'un scénario :
- Charger les variables d'environnement (si la variable NOM_SCENARIO n'est pas chargée, il faut arrêter le scénario mais on ne peut pas renvoyer de message car on a pas encore fait d'appel API)
- Charger le fichier de configuration du scénario (ce fichier est obligatoire car il contient l'identifiant unique du scénario qui permets de requêter l'API de Lecture de données)
- Si la variable d'environnement LECTURE est true alors il faut faire appelle à l'API de lecture.
- Si l'API de lecture renvoie des données alors il faut lire le planning d'execution et vérifier si le scénario respecte bien le planning (jours férie, plage horaire)

