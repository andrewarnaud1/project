# Tableau Complet des Variables du Simulateur

## 🎯 **Vue d’Ensemble**

Ce tableau recense **TOUTES** les variables de votre simulateur :

- **Sources d’initialisation** (env, config, API, calculé)
- **Règles de priorité** entre sources
- **Utilisation** dans le code
- **Valeurs par défaut**

-----

## 📊 **Tableau Principal (32 Variables)**

|#                       |**Variable**              |**Type**        |**Sources**                         |**Priorité**                               |**Défaut**          |**Utilisation**                  |**Fichiers Concernés**                               |
|------------------------|--------------------------|----------------|------------------------------------|-------------------------------------------|--------------------|---------------------------------|-----------------------------------------------------|
|                        |                          |                |                                    |                                           |                    |                                 |                                                     |
|**🏷️ IDENTIFICATION**    |                          |                |                                    |                                           |                    |                                 |                                                     |
|1                       |`nom_scenario`            |`str`           |env, api                            |API > env                                  |`""`                |Nom affiché, chemins, logs       |environnement.py, configuration.py, initialisation.py|
|2                       |`identifiant`             |`str`           |config_scenario                     |config_scenario                            |`""`                |Clé unique API, traçabilité      |configuration.py, api_lecture.py                     |
|3                       |`type_scenario`           |`ScenarioType`  |config_scenario                     |config_scenario                            |`WEB`               |Logique spécialisée (Exadata/Web)|environnement.py, initialisation.py                  |
|                        |                          |                |                                    |                                           |                    |                                 |                                                     |
|**🌍 PLATEFORME**        |                          |                |                                    |                                           |                    |                                 |                                                     |
|4                       |`plateforme`              |`PlateformeEnum`|env                                 |env                                        |`PROD`              |Sélection config par plateforme  |environnement.py, configuration.py                   |
|                        |                          |                |                                    |                                           |                    |                                 |                                                     |
|**🌐 NAVIGATION**        |                          |                |                                    |                                           |                    |                                 |                                                     |
|5                       |`navigateur`              |`NavigateurEnum`|env                                 |env                                        |`FIREFOX`           |Lancement Playwright             |environnement.py, contexte.py                        |
|6                       |`headless`                |`bool`          |env                                 |env                                        |`False`             |Options Playwright               |environnement.py, contexte.py                        |
|7                       |`proxy`                   |`str?`          |env, config_scenario, config_commune|env > scenario > commune                   |`None`              |Configuration réseau             |navigateur.py, contexte.py                           |
|8                       |`generer_har`             |`bool`          |api, config_scenario                |API flag_har OU config                     |`False`             |Enregistrement réseau            |generation_har.py, contexte.py                       |
|                        |                          |                |                                    |                                           |                    |                                 |                                                     |
|**📁 CHEMINS BASE**      |                          |                |                                    |                                           |                    |                                 |                                                     |
|9                       |`simu_path`               |`Path`          |env                                 |env                                        |`/opt/simulateur_v6`|Chemin installation simulateur   |environnement.py, constantes.py                      |
|10                      |`scenarios_path`          |`Path`          |env                                 |env                                        |`/opt/scenarios_v6` |Chemin scénarios et configs      |environnement.py, configuration.py                   |
|11                      |`output_path`             |`Path`          |env                                 |env                                        |`/var/simulateur_v6`|Racine rapports/screenshots      |environnement.py, initialisation.py                  |
|12                      |`screenshot_dir`          |`Path?`         |calculé                             |`output_path` + date/heure                 |`None`              |Stockage captures d’écran        |initialisation.py, screenshot_manager.py             |
|13                      |`report_dir`              |`Path?`         |calculé                             |`output_path` + date/heure                 |`None`              |Stockage rapports JSON           |initialisation.py, execution.py                      |
|14                      |`chemin_images_exadata`   |`Path?`         |calculé                             |`scenarios_path` si Exadata                |`None`              |Images reconnaissance Exadata    |initialisation.py, scenarios_exadata/                |
|                        |                          |                |                                    |                                           |                    |                                 |                                                     |
|**🔗 API**               |                          |                |                                    |                                           |                    |                                 |                                                     |
|15                      |`lecture`                 |`bool`          |env                                 |env                                        |`True`              |Activation lecture API           |environnement.py, initialisation.py                  |
|16                      |`inscription`             |`bool`          |env, dépend lecture                 |Si lecture=True ALORS True SINON env       |`True`              |Activation écriture API          |environnement.py, execution.py                       |
|17                      |`url_base_api_injecteur`  |`str`           |env                                 |env                                        |`localhost`         |URL API injecteur                |environnement.py, api_*.py                           |
|18                      |`url_initiale`            |`str?`          |config_scenario, config_commune     |scenario > commune                         |`None`              |Point d’entrée application       |configuration.py, tests scénarios                    |
|                        |                          |                |                                    |                                           |                    |                                 |                                                     |
|**👤 UTILISATEUR**       |                          |                |                                    |                                           |                    |                                 |                                                     |
|19                      |`utilisateur_isac`        |`str?`          |config_scenario                     |scenario                                   |`None`              |Nom fichier utilisateur à charger|configuration.py, recuperation_utilisateur.py        |
|20                      |`utilisateur`             |`str?`          |config_scenario, fichier ISAC       |déchiffrement ISAC                         |`None`              |Login pour authentification      |recuperation_utilisateur.py, tests                   |
|21                      |`mot_de_passe`            |`str?`          |config_scenario, fichier ISAC       |déchiffrement ISAC                         |`None`              |Password pour authentification   |recuperation_utilisateur.py, decrypt.py              |
|                        |                          |                |                                    |                                           |                    |                                 |                                                     |
|**⚙️ SPÉCIALISÉ**        |                          |                |                                    |                                           |                    |                                 |                                                     |
|22                      |`nom_vm_windows`          |`str?`          |env, config_scenario                |env > scenario                             |`None`              |VM Guacamole pour Exadata        |environnement.py                                     |
|23                      |`nom_application`         |`str`           |api, config_scenario, config_commune|API > scenario > commune                   |`NO_API`            |Nom app pour chemins             |rotation.py, initialisation.py                       |
|                        |                          |                |                                    |                                           |                    |                                 |                                                     |
|**💻 SYSTÈME**           |                          |                |                                    |                                           |                    |                                 |                                                     |
|24                      |`playwright_browsers_path`|`Path`          |env                                 |env                                        |`/browsers`         |Chemin navigateurs Playwright    |environnement.py, contexte.py                        |
|25                      |`utilisateur_isac_path`   |`Path`          |env, calculé                        |env OU `scenarios_path`/config/utilisateurs|calculé             |Chemin fichiers utilisateurs     |environnement.py, recuperation_utilisateur.py        |
|26                      |`config_commune`          |`str?`          |config_scenario                     |scenario                                   |`None`              |Nom fichier config commune       |configuration.py                                     |
|27                      |`injecteur`               |`str`           |calculé                             |`socket.gethostname()`                     |`unknown`           |Nom machine pour rapports        |execution.py                                         |
|28                      |`interface_ip`            |`str`           |calculé                             |`socket.gethostbyname()`                   |`127.0.0.1`         |IP machine pour rapports         |execution.py                                         |
|                        |                          |                |                                    |                                           |                    |                                 |                                                     |
|**🌐 NAVIGATION AVANCÉE**|                          |                |                                    |                                           |                    |                                 |                                                     |
|29                      |`http_credentials`        |`dict?`         |config_scenario, config_commune     |scenario > commune                         |`None`              |Auth HTTP basique                |navigateur.py, contexte.py                           |
|30                      |`cookies`                 |`str?`          |config_scenario, config_commune     |scenario > commune                         |`None`              |Nom fichier cookies              |navigateur.py, contexte.py                           |
|31                      |`plein_ecran`             |`bool`          |config_scenario, config_commune     |scenario > commune                         |`False`             |Lancement navigateur             |navigateur.py, contexte.py                           |
|                        |                          |                |                                    |                                           |                    |                                 |                                                     |
|**🔧 OPTIONNELS**        |                          |                |                                    |                                           |                    |                                 |                                                     |
|32                      |`fichiers_erreurs`        |`list`          |config_scenario                     |scenario                                   |`[]`                |Patterns détection erreurs       |timeout_checker.py                                   |

-----

## 📋 **Détails par Catégorie**

### **🏷️ IDENTIFICATION (3 variables)**

#### **nom_scenario**

```python
# Initialisation
env: NOM_SCENARIO="mon_scenario"
api: {"nom": "scenario_depuis_api"}

# Règle de priorité
nom_scenario = api_data.get('nom') or env_data.get('nom_scenario') or ""

# Utilisation
- Chargement fichier config: f"{nom_scenario}.conf"
- Chemins screenshots: f".../{nom_scenario}/..."
- Logs et rapports
- Titre des captures d'écran
```

#### **identifiant**

```python
# Initialisation
config_scenario: identifiant: "SCEN_001"

# Règle de priorité
identifiant = config_scenario_data.get('identifiant', '')

# Utilisation
- Clé unique pour appels API
- Traçabilité dans rapports
- Liens entre exécutions
```

#### **type_scenario**

```python
# Initialisation
config_scenario: type_scenario: "exadata" | "web" | "technique"

# Règle de priorité
type_scenario = ScenarioType(config_scenario_data.get('type_scenario', 'web'))

# Utilisation
- Logique conditionnelle (images Exadata)
- Validation variables spécifiques
- Choix actions automatisées
```

### **🌐 NAVIGATION (4 variables)**

#### **navigateur**

```python
# Initialisation
env: NAVIGATEUR="firefox" | "chromium" | "msedge"

# Règle de priorité
navigateur = NavigateurEnum(env_data.get('navigateur', 'firefox'))

# Utilisation
- contexte.py: p.firefox.launch() vs p.chromium.launch()
- Options spécifiques par navigateur
```

#### **headless**

```python
# Initialisation  
env: HEADLESS="true" | "false" | "1" | "0"

# Règle de priorité
headless = convert_to_bool(env_data.get('headless', 'false'))

# Utilisation
- contexte.py: browser.launch(headless=headless)
- Mode debug vs production
```

#### **proxy**

```python
# Initialisation
env: PROXY="http://proxy:8080" | "http://proxy.pac"
config_scenario: proxy: "http://specific-proxy:3128"
config_commune: proxy: "http://common-proxy:8080"

# Règle de priorité
proxy = env_data.get('proxy') or config_scenario_data.get('proxy') or config_commune_data.get('proxy')

# Utilisation
- navigateur.py: options["proxy"] = {"server": proxy}
- Configuration réseau spécifique
```

#### **generer_har**

```python
# Initialisation
api: {"flag_har": true}
config_scenario: generer_har: true

# Règle de priorité (logique spéciale)
if api_data:
    generer_har = api_data.get("flag_har", False)
else:
    generer_har = config_scenario_data.get("generer_har", False)

# Utilisation
- contexte.py: context.tracing.start() si generer_har
- Enregistrement traces réseau
```

### **📁 CHEMINS (6 variables)**

#### **Chemins de base (3)**

```python
# simu_path
env: SIMU_PATH="/opt/simulateur_v6"
Usage: Chemin installation, scripts utilitaires

# scenarios_path  
env: SCENARIOS_PATH="/opt/scenarios_v6"
Usage: Base pour config/, scenarios/, images/

# output_path
env: OUTPUT_PATH="/var/simulateur_v6" 
Usage: Racine pour screenshots/, rapports/
```

#### **Chemins calculés (3)**

```python
# screenshot_dir
Calcul: f"{output_path}/screenshots/{nom_app}/{nom_scenario}/{date}/{heure}"
Usage: screenshot_manager.py pour stockage captures

# report_dir
Calcul: f"{output_path}/rapports/{nom_app}/{nom_scenario}/{date}/{heure}"
Usage: execution.py pour rapports JSON

# chemin_images_exadata  
Calcul: f"{scenarios_path}/scenarios_exadata/images/{nom_scenario}" (si type=exadata)
Usage: scenarios_exadata/ pour reconnaissance d'images
```

### **🔗 API (4 variables)**

#### **lecture/inscription**

```python
# lecture
env: LECTURE="true"
Usage: Activation appels lecture_api_scenario()

# inscription (logique dépendante)
if lecture == True:
    inscription = True  # Forcé
else:
    inscription = convert_to_bool(env_data.get('inscription', 'true'))
Usage: Activation appels inscrire_resultats_api()
```

#### **URLs**

```python
# url_base_api_injecteur
env: URL_BASE_API_INJECTEUR="http://192.168.1.100/"
Usage: Base pour tous appels API injecteur

# url_initiale
config_scenario: url_initiale: "https://mon-app.com/login"
config_commune: url_initiale: "https://common-app.com"
Usage: page.goto(url_initiale) dans tests
```

### **👤 UTILISATEUR (3 variables)**

#### **Chargement utilisateur ISAC**

```python
# utilisateur_isac
config_scenario: utilisateur_isac: "user_test"
Usage: Déclenche chargement fichier config/utilisateurs/user_test.conf

# utilisateur + mot_de_passe
Chargement: recuperer_utlisateur_isac() depuis fichier ISAC
Déchiffrement: decrypt.py si crypté
Usage: Authentification dans tests
```

### **⚙️ SPÉCIALISÉ (2 variables)**

#### **nom_vm_windows**

```python
# Initialisation
env: NOM_VM_WINDOWS="1 - Windows 11 POCv6 (.40)"
config_scenario: nom_vm_windows: "VM-Test-Exadata"

# Usage
- Connexion Guacamole pour scénarios Exadata
- Sélection VM spécifique
```

#### **nom_application**

```python
# Initialisation
api: {"application": {"nom": "MonApp"}}
config_scenario: nom_application: "AppScenario"
config_commune: nom_application: "AppCommune"

# Usage
- Chemins: screenshots/{nom_application}/
- Rotation données: cache/{nom_application}/
```

### **💻 SYSTÈME (5 variables)**

#### **Chemins système**

```python
# playwright_browsers_path
env: PLAYWRIGHT_BROWSERS_PATH="/home/user/.cache/ms-playwright"
Usage: Variable d'environnement Playwright

# utilisateur_isac_path
env: UTILISATEURS_ISAC_PATH="/custom/path/users"
Défaut: f"{scenarios_path}/config/utilisateurs"
Usage: Localisation fichiers utilisateurs

# config_commune
config_scenario: config_commune: "base"
Usage: Déclenche chargement config/commun/base.conf
```

#### **Informations machine**

```python
# injecteur
Calcul: socket.gethostname()
Usage: Identification machine dans rapports

# interface_ip  
Calcul: socket.gethostbyname(socket.gethostname())
Usage: IP machine dans rapports
```

### **🌐 NAVIGATION AVANCÉE (3 variables)**

#### **Authentification et cookies**

```python
# http_credentials
config_scenario/commune: 
  http_credentials:
    utilisateur: "admin"
    mot_de_passe: "secret"
Usage: context.new_context(http_credentials=credentials)

# cookies
config_scenario: cookies: "session_cookies"
Usage: Chargement cookies/{cookies}.json

# plein_ecran
config_scenario: plein_ecran: true
Usage: options["args"] = ["--start-maximized"]
```

### **🔧 OPTIONNELS (1 variable)**

#### **fichiers_erreurs**

```python
# Initialisation
config_scenario:
  fichiers_erreurs:
    - "erreurs_app1"
    - "erreurs_specifiques"

# Usage
timeout_checker.py: Chargement patterns depuis config/erreurs_app1.yaml
Détection erreurs applicatives lors timeouts
```

-----

## 📊 **Analyse Statistique**

### **Par Source d’Initialisation**

- **Environnement uniquement** : 12 variables (37%)
- **Config scénario uniquement** : 7 variables (22%)
- **Priorité multiple** : 6 variables (19%)
- **Calculé automatiquement** : 5 variables (16%)
- **Logique spéciale** : 2 variables (6%)

### **Par Type de Donnée**

- **String** : 14 variables
- **Path** : 8 variables
- **Boolean** : 5 variables
- **Enum** : 3 variables
- **Dict/List** : 2 variables

### **Par Criticité**

- **Obligatoires** : nom_scenario, identifiant, type_scenario
- **Techniques** : chemins, navigateur, API
- **Optionnelles** : proxy, cookies, fichiers_erreurs

-----

## 🔄 **Cycle de Vie des Variables**

### **Phase 1 : Chargement Sources**

```python
1. env_data = load_environment_variables()
2. config_scenario_data = load_scenario_config()  
3. config_commune_data = load_common_config()
4. api_data = load_api_data()
```

### **Phase 2 : Application Règles**

```python
for each variable:
    apply_priority_rule()  # 32 règles spécifiques
```

### **Phase 3 : Calculs Dérivés**

```python
calculate_derived_paths()  # screenshot_dir, report_dir, etc.
```

### **Phase 4 : Utilisation**

```python
# Pendant l'exécution des tests
browser.launch(headless=scenario.headless)
page.goto(scenario.url_initiale)
screenshot_manager.save(scenario.screenshot_dir)
```