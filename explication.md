# Flux d’Inscription API - Envoi des Données JSON

## Vue d’Ensemble des Moments d’Inscription

Il y a **3 moments** où des données JSON peuvent être envoyées à l’API d’inscription :

```
┌─ MOMENT 1: ERREUR D'INITIALISATION ─┐
│  Module: initialisation.py           │
│  Quand: Phases 5-6 (post-API)        │
│  Status: 3 (UNKNOWN)                 │
│  Méthode: _inscrire_erreur_init...() │
└───────────────────────────────────────┘

┌─ MOMENT 2: SUCCÈS OU ÉCHEC TESTS ────┐
│  Module: execution.py                 │
│  Quand: Finalisation (fixture)       │
│  Status: 0, 1, 2 (selon résultats)   │
│  Méthode: inscrire_resultats_api()   │
└───────────────────────────────────────┘

┌─ MOMENT 3: ERREUR FINALISATION ──────┐
│  Module: execution.py                 │
│  Quand: Exception en finalisation    │
│  Status: 2 (ERREUR)                  │
│  Méthode: inscrire_resultats_api()   │
└───────────────────────────────────────┘
```

## MOMENT 1 : Erreur d’Initialisation

### 📍 **Où ça se passe**

```python
# Dans initialisation.py
class InitialisateurScenario:
    def _gerer_erreur_post_api(self, erreur):
        self._inscrire_erreur_initialisation(str(erreur))
```

### 🔍 **Conditions d’Inscription**

```python
def _inscrire_erreur_initialisation(self, message_erreur: str):
    # 1. Vérifier si API chargée
    if not self.api_chargee_avec_succes:
        return  # Pas d'inscription
        
    # 2. Vérifier si identifiant disponible
    identifiant = self.config.get("identifiant")
    if not identifiant:
        return  # Pas d'inscription
        
    # 3. Vérifier si inscription activée
    if not self.config.get("inscription"):
        return  # Pas d'inscription
    
    # ✅ Toutes les conditions OK → Inscription
```

### 📤 **JSON Envoyé (Status=3)**

```json
{
  "identifiant": "SCENARIO_123",
  "scenario": "test_connexion_app",
  "date": "2025-01-15T14:30:00.123456",
  "duree": 0.052,
  "status": 3,
  "nb_scene": 0,
  "commentaire": "Erreur lors de l'initialisation du scénario - Scénario non lancé",
  "injecteur": "jenkins-worker-01",
  "navigateur": "firefox",
  "interface_ip": "127.0.0.1",
  "status_initial": 3,
  "commentaire_initial": "Erreur lors de l'initialisation du scénario - Scénario non lancé",
  "briques": []
}
```

### 🚨 **Cas d’Erreur d’Initialisation**

```python
# Exemples de phases qui déclenchent cette inscription :
# Phase 5: Échec finalisation configuration
# Phase 6: Échec création contexte navigateur
# Exception inattendue après API chargée

try:
    self._phase_5_configuration_finale()
    self._phase_6_repertoires()
except Exception as e:
    # → ErreurPostAPI → _inscrire_erreur_initialisation()
    raise ErreurPostAPI(f"Échec finalisation: {e}")
```

## MOMENT 2 : Résultats Normaux (Succès/Échec Tests)

### 📍 **Où ça se passe**

```python
# Dans execution.py - fixture pytest
@pytest.fixture(scope="session")
def execution():
    execution_scenario = Execution()
    yield execution_scenario
    
    # === FINALISATION ===
    execution_scenario.finalise()  # Calcule status/durée
    json_execution = execution_scenario.save_to_json(...)
    
    if execution_scenario.config.get("inscription"):
        inscrire_resultats_api(
            execution_scenario.config["url_base_api_injecteur"],
            json_execution
        )
```

### 📤 **JSON Envoyé (Status selon résultats)**

```json
{
  "identifiant": "SCENARIO_123",
  "scenario": "test_connexion_app",
  "date": "2025-01-15T14:30:00.123456",
  "duree": 45.238,
  "status": 0,  // 0=OK, 1=WARNING, 2=ERROR
  "nb_scene": 5,
  "commentaire": "Test réussi - Connexion validée",
  "injecteur": "jenkins-worker-01",
  "navigateur": "firefox",
  "interface_ip": "127.0.0.1",
  "status_initial": 0,
  "commentaire_initial": "Test réussi - Connexion validée",
  "briques": [
    {
      "nom": "ouverture_page",
      "ordre": 1,
      "date": "2025-01-15T14:30:05.000000",
      "duree": "2.150",
      "status": 0,
      "url": "https://app.example.com/login",
      "commentaire": "Page ouverte avec succès"
    },
    // ... autres étapes
  ]
}
```

## MOMENT 3 : Erreur de Finalisation

### 📍 **Où ça se passe**

```python
# Dans execution.py - fixture pytest
@pytest.fixture(scope="session")
def execution():
    # ... tests exécutés ...
    
    try:
        execution_scenario.finalise()
        # ... inscription normale ...
    except Exception as e:
        # 🚨 ERREUR DE FINALISATION
        if execution_scenario.config.get("inscription"):
            json_erreur = {
                "identifiant": execution_scenario.config.get("identifiant", ""),
                "status": 2,  # ERREUR
                "commentaire": f"Erreur lors de la finalisation: {e}",
                # ... autres champs
            }
            inscrire_resultats_api(..., json_erreur)
```

## Fonction d’Inscription API Commune

### 🔧 **Implémentation dans `api.py`**

```python
def inscrire_resultats_api(url_base_api_injecteur: str, data: dict) -> None:
    """
    Inscrit les résultats du scénario dans l'API.
    """
    url = f"{url_base_api_injecteur}injapi/scenario/execution"
    
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "text/plain",
    }
    
    try:
        response = requests.post(
            url, 
            headers=headers, 
            timeout=10, 
            json=data  # ← Le JSON est envoyé ici
        )
        response.raise_for_status()
        
        LOGGER.info("✅ Inscription API réussie: %s", response.text)
        
    except Exception as erreur:
        LOGGER.error("❌ Échec inscription API: %s", erreur)
        # En cas d'échec, pas de nouvelle exception levée
```

## Matrice de Décision d’Inscription

|Situation          |API Chargée|Identifiant|Inscription ON|→ Action                    |
|-------------------|-----------|-----------|--------------|----------------------------|
|Phase 1-4 erreur   |❌          |❌          |❌             |**Pas d’inscription**       |
|Phase 5-6 erreur   |✅          |✅          |✅             |**Inscription status=3**    |
|Phase 5-6 erreur   |✅          |❌          |✅             |**Pas d’inscription**       |
|Phase 5-6 erreur   |✅          |✅          |❌             |**Pas d’inscription**       |
|Tests OK/KO        |✅          |✅          |✅             |**Inscription status=0/1/2**|
|Tests OK/KO        |✅          |✅          |❌             |**Log JSON local**          |
|Finalisation erreur|✅          |✅          |✅             |**Inscription status=2**    |

## Logs et Debug

### 📋 **Messages de Log selon les Cas**

```python
# Inscription réussie
"✅ Erreur d'initialisation inscrite en base"
"✅ Résultats inscrits en API"

# Inscription impossible
"⚠️ API non chargée - Pas d'inscription"
"⚠️ Identifiant scénario non disponible - Pas d'inscription"  
"⚠️ Inscription désactivée"

# Inscription échouée
"❌ Échec inscription: ConnectionError..."
"📄 Données d'erreur:" + JSON dump local
```

### 🔍 **Fallback en Cas d’Échec API**

```python
try:
    inscrire_resultats_api(url, data)
except Exception as e:
    # L'inscription échoue → Pas de crash
    LOGGER.error("Échec inscription: %s", e)
    
    # Dump JSON en local pour debug
    print("📄 Données qui devaient être inscrites:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
```

## Résumé du Flux

1. **Initialisation** : Module d’initialisation peut inscrire des erreurs (status=3)
1. **Exécution** : Tests normaux → inscription des résultats (status=0/1/2)
1. **Finalisation** : En cas d’erreur → inscription d’erreur (status=2)
1. **Fallback** : Si inscription impossible → logs + dump JSON local

Cette architecture garantit qu’aucune donnée incomplète n’est envoyée à l’API, tout en conservant les informations pour le debug.