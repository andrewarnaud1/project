Je vais vous guider pour créer un projet complet avec une structure professionnelle, incluant un environnement virtuel, des fonctions et classes réutilisables, un fichier `README.md`, et une organisation claire du code.

---

## Structure du projet

Voici la structure du projet que nous allons créer :

```
automation_project/
│
├── .env/                   # Environnement virtuel (à créer)
├── logs/                   # Dossier pour les logs
├── src/
│   ├── __init__.py
│   ├── browser_automation.py  # Module pour l'automatisation du navigateur
│   ├── windows_automation.py  # Module pour l'automatisation de l'application Windows
│   ├── database.py         # Module pour interagir avec PostgreSQL
│   ├── config.py           # Configuration du projet
│   └── main.py             # Point d'entrée du script
│
├── requirements.txt        # Dépendances du projet
├── README.md               # Documentation du projet
└── .gitignore              # Fichier pour ignorer certains fichiers/dossiers
```

---

## Étape 1 : Créer l'environnement virtuel

1. Ouvrez un terminal et naviguez vers le dossier où vous souhaitez créer le projet.
2. Créez un environnement virtuel :

   ```bash
   python -m venv .env
   ```

3. Activez l'environnement virtuel :
   - Sur Windows :
     ```bash
     .env\Scripts\activate
     ```
   - Sur macOS/Linux :
     ```bash
     source .env/bin/activate
     ```

4. Installez les dépendances nécessaires :

   ```bash
   pip install playwright pywinauto psycopg2 python-dotenv
   ```

5. Initialisez Playwright :

   ```bash
   playwright install
   ```

---

## Étape 2 : Créer les fichiers du projet

### 1. `requirements.txt`

Listez les dépendances du projet :

```
playwright
pywinauto
psycopg2
python-dotenv
```

### 2. `src/config.py`

Stockez les configurations du projet (comme les identifiants de connexion) :

```python
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de la base de données PostgreSQL
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "votre_base_de_donnees"),
    "user": os.getenv("DB_USER", "votre_utilisateur"),
    "password": os.getenv("DB_PASSWORD", "votre_mot_de_passe"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

# Configuration du navigateur
BROWSER_CONFIG = {
    "headless": False,  # Mettez True pour exécuter en mode headless
    "url": os.getenv("APP_URL", "https://votre-url-de-connexion.com"),
    "username": os.getenv("APP_USERNAME", "votre_identifiant"),
    "password": os.getenv("APP_PASSWORD", "votre_mot_de_passe"),
}

# Configuration de l'application Windows
WINDOWS_APP_CONFIG = {
    "app_title": os.getenv("APP_TITLE", "Titre de la fenêtre de l'application"),
    "button_name": os.getenv("BUTTON_NAME", "Nom du bouton"),
}
```

### 3. `src/database.py`

Créez un module pour interagir avec PostgreSQL :

```python
import psycopg2
from .config import DB_CONFIG

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

    def enregistrer_resultat(self, test_reussi):
        try:
            query = "INSERT INTO resultats_tests (date_test, reussi) VALUES (%s, %s);"
            self.cursor.execute(query, (time.strftime('%Y-%m-%d %H:%M:%S'), test_reussi))
            self.conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'enregistrement dans la base de données : {e}")

    def close(self):
        self.cursor.close()
        self.conn.close()
```

### 4. `src/browser_automation.py`

Créez un module pour l'automatisation du navigateur :

```python
from playwright.sync_api import sync_playwright
from .config import BROWSER_CONFIG

class BrowserAutomation:
    def __init__(self):
        self.browser_config = BROWSER_CONFIG

    def lancer_application(self):
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=self.browser_config["headless"])
            page = browser.new_page()
            page.goto(self.browser_config["url"])
            time.sleep(2)

            # Remplir les champs de connexion
            page.fill("#username", self.browser_config["username"])
            page.fill("#password", self.browser_config["password"])
            page.click("#submit-button")
            time.sleep(2)

            # Lancer l'application Windows
            page.click("#lancer-application")
            time.sleep(5)

            browser.close()
```

### 5. `src/windows_automation.py`

Créez un module pour l'automatisation de l'application Windows :

```python
from pywinauto import Application
from .config import WINDOWS_APP_CONFIG

class WindowsAutomation:
    def __init__(self):
        self.windows_config = WINDOWS_APP_CONFIG

    def interagir_avec_application(self):
        try:
            app = Application(backend="win32").connect(title=self.windows_config["app_title"])
            fenetre = app.window(title=self.windows_config["app_title"])
            fenetre.wait("ready", timeout=10)

            # Cliquer sur un bouton
            fenetre.Button(name=self.windows_config["button_name"]).click()

            # Vérifier la présence d'un élément
            element_present = fenetre.exists(timeout=5)
            return element_present

        except Exception as e:
            print(f"Erreur lors de l'interaction avec l'application Windows : {e}")
            return False

        finally:
            app.kill()
```

### 6. `src/main.py`

Point d'entrée du script :

```python
import time
from .browser_automation import BrowserAutomation
from .windows_automation import WindowsAutomation
from .database import Database

def executer_test():
    # Automatisation du navigateur
    browser = BrowserAutomation()
    browser.lancer_application()

    # Automatisation de l'application Windows
    windows = WindowsAutomation()
    test_reussi = windows.interagir_avec_application()

    # Enregistrer le résultat dans la base de données
    db = Database()
    db.enregistrer_resultat(test_reussi)
    db.close()

if __name__ == "__main__":
    while True:
        executer_test()
        time.sleep(600)  # Attendre 10 minutes avant la prochaine exécution
```

---

## Étape 3 : Créer le fichier `README.md`

Documentez votre projet :

```markdown
# Automation Project

Ce projet permet d'automatiser les tests d'une application JVM lancée via un navigateur et contrôlée au niveau du système d'exploitation.

## Prérequis

- Python 3.8+
- PostgreSQL
- Playwright
- PyWinAuto

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/automation_project.git
   ```

2. Créez et activez un environnement virtuel :
   ```bash
   python -m venv .env
   source .env/bin/activate  # Sur macOS/Linux
   .env\Scripts\activate     # Sur Windows
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

4. Configurez les variables d'environnement dans un fichier `.env` :
   ```env
   DB_NAME=votre_base_de_donnees
   DB_USER=votre_utilisateur
   DB_PASSWORD=votre_mot_de_passe
   DB_HOST=localhost
   DB_PORT=5432
   APP_URL=https://votre-url-de-connexion.com
   APP_USERNAME=votre_identifiant
   APP_PASSWORD=votre_mot_de_passe
   APP_TITLE=Titre de la fenêtre de l'application
   BUTTON_NAME=Nom du bouton
   ```

## Exécution

Lancez le script principal :
```bash
python src/main.py
```

## Structure du projet

- `src/` : Contient les modules Python.
- `logs/` : Dossier pour les logs.
- `.env/` : Environnement virtuel.
- `README.md` : Documentation du projet.
```

---

## Étape 4 : Créer le fichier `.gitignore`

Ignorez les fichiers/dossiers inutiles :

```
.env/
logs/
__pycache__/
*.pyc
*.pyo
*.pyd
*.db
*.sqlite3
```

---

## Étape 5 : Tester le projet

1. Activez l'environnement virtuel.
2. Exécutez le script principal :
   ```bash
   python src/main.py
   ```

---

Vous avez maintenant un projet complet, bien structuré et prêt à être utilisé ou étendu ! 🚀
