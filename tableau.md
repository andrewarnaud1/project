# Tableau des variables du simulateur

|Variable                |Sources                             |Priorité                                 |Défaut            |Explications                                   |
|------------------------|------------------------------------|-----------------------------------------|------------------|-----------------------------------------------|
|nom_scenario            |env, api                            |API > env                                |None              |Nom du scénario à exécuter                     |
|identifiant             |config_scenario                     |config_scenario                          |None              |Identifiant unique pour l’API                  |
|type_scenario           |config_scenario                     |config_scenario                          |WEB               |Type de scénario (web/exadata/technique)       |
|plateforme              |env                                 |env                                      |PROD              |Environnement d’exécution (dev/test/prod)      |
|navigateur              |env                                 |env                                      |FIREFOX           |Navigateur à utiliser (firefox/chromium/msedge)|
|headless                |env                                 |env                                      |False             |Mode sans interface graphique                  |
|proxy                   |env, config_scenario, config_commune|env > scenario > commune                 |None              |Configuration proxy                            |
|generer_har             |api, config_scenario                |API flag_har OU config                   |False             |Génération fichier HAR                         |
|simu_path               |env                                 |env                                      |/opt/simulateur_v6|Chemin installation simulateur                 |
|scenarios_path          |env                                 |env                                      |/opt/scenarios_v6 |Chemin des scénarios                           |
|output_path             |env                                 |env                                      |/var/simulateur_v6|Chemin de sortie rapports                      |
|screenshot_dir          |calculé                             |output_path + date/heure                 |None              |Répertoire captures d’écran                    |
|report_dir              |calculé                             |output_path + date/heure                 |None              |Répertoire rapports JSON                       |
|chemin_images_exadata   |calculé                             |scenarios_path si Exadata                |None              |Chemin images reconnaissance                   |
|lecture                 |env                                 |env                                      |True              |Activation lecture API                         |
|inscription             |env, dépend lecture                 |Si lecture=True alors True sinon env     |True              |Activation écriture API                        |
|url_base_api_injecteur  |env                                 |env                                      |localhost         |URL de base API injecteur                      |
|url_initiale            |config_scenario, config_commune     |scenario > commune                       |None              |URL d’entrée application                       |
|utilisateur_isac        |config_scenario                     |config_scenario                          |None              |Nom fichier utilisateur ISAC                   |
|utilisateur             |config_scenario, fichier ISAC       |déchiffrement ISAC                       |None              |Login pour authentification (déchifré)         |
|mot_de_passe            |config_scenario, fichier ISAC       |déchiffrement ISAC                       |None              |Mot de passe pour authentification (déchifré)  |
|nom_vm_windows          |env, config_scenario                |env > scenario                           |None              |Nom VM Windows pour Exadata                    |
|nom_application         |api, config_scenario, config_commune|API > scenario > commune                 |NO_API            |Nom application pour chemins                   |
|playwright_browsers_path|env                                 |env                                      |/browsers         |Chemin navigateurs Playwright                  |
|utilisateur_isac_path   |calculé                             |scenarios_path/config/utilisateurs       |calculé           |Chemin fichiers utilisateurs                   |
|config_commune          |config_scenario                     |config_scenario                          |None              |Nom fichier config commune                     |
|injecteur               |calculé                             |socket.gethostname()                     |inconnu           |Nom machine pour rapports                      |
|interface_ip            |calculé                             |socket.gethostbyname()                   |127.0.0.1         |IP machine pour rapports                       |
|http_credentials        |config_scenario, config_commune     |scenario > commune                       |None              |Authentification HTTP basique                  |
|cookies                 |config_scenario, config_commune     |scenario > commune                       |None              |Nom fichier cookies                            |
|plein_ecran             |config_scenario, config_commune     |scenario > commune                       |False             |Lancement navigateur plein écran               |
|fichiers_erreurs        |config_scenario                     |config_scenario                          |[]                |Liste fichiers patterns erreurs                |
|execution_date_debut    |calculé                             |datetime.now() au chargement             |now               |Horodatage pour chemins                        |
