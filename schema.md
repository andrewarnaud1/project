# Flux d'Exécution Séquentiel - Classe Execution Refactorisée

## Vue d'Ensemble

```
Execution.__init__()
    ↓
┌─────────────────────────────────────────────────────────────┐
│                    PHASES 1-3 : PRÉ-API                    │
│                 (Erreurs = exit 1, pas d'inscription)      │
└─────────────────────────────────────────────────────────────┘
    ↓
_phase_1_environnement()
    ├─ ✅ Variables d'environnement chargées
    └─ ❌ ErreurPreExecution → exit 1, pas d'inscription
    ↓
_phase_2_api_lecture()
    ├─ 🔍 LECTURE=false → Continuer sans API
    ├─ ✅ API chargée → api_chargee_avec_succes = True
    └─ ❌ Échec API → ErreurPreExecution → exit 1, pas d'inscription
    ↓
_phase_3_verification_planning()
    ├─ 🔍 Pas d'API → Continuer
    ├─ ✅ Planning respecté → Continuer
    └─ ❌ Planning non respecté → ErreurPreExecution → exit 1, pas d'inscription
    ↓
┌─────────────────────────────────────────────────────────────┐
│                   PHASES 4-5 : POST-API                    │
│            (Erreurs = exit 2, inscription status=3)        │
└─────────────────────────────────────────────────────────────┘
    ↓
_phase_4_configuration()
    ├─ ✅ Configuration créée → Continuer
    └─ ❌ Échec config → ErreurPostAPI 
        ├─ ✅ API + identifiant OK → Inscription + exit 2
        └─ ❌ Pas d'identifiant → Log warning + exit 2
    ↓
_phase_5_repertoires()
    ├─ ✅ Répertoires créés → Initialisation terminée
    └─ ❌ Échec répertoires → Warning, continuer
    ↓
🎉 EXECUTION PRÊTE POUR LES TESTS
```

## Règles d'Inscription par Phase

### ❌ JAMAIS D'INSCRIPTION (ErreurPreExecution)

| Phase | Cause | Action |
|-------|-------|--------|
| 1 | Variables environnement manquantes | exit 1, log erreur |
| 2 | Échec API de lecture | exit 1, log erreur |
| 3 | Planning non respecté | exit 1, log erreur |

**Logique** : Si l'API n'est pas chargée ou le planning interdit l'exécution, aucune donnée ne doit être envoyée.

### ✅ INSCRIPTION OBLIGATOIRE (ErreurPostAPI) - AVEC CONDITIONS

| Phase | Cause | Conditions d'inscription | Action |
|-------|-------|-------------------------|--------|
| 4 | Échec création configuration | API + identifiant OK | Inscription status=3 + exit 2 |
| 5 | Échec contexte navigateur | API + identifiant OK | Inscription status=3 + exit 2 |

**Conditions obligatoires pour l'inscription** :
1. ✅ API chargée avec succès (`api_chargee_avec_succes = True`)
2. ✅ Identifiant scénario disponible (`identifiant` non vide)
3. ✅ Inscription activée (`inscription = True`)

**Si une condition manque** → Pas d'inscription, log d'avertissement

### 🔍 VÉRIFICATIONS D'INSCRIPTION

```python
def _peut_inscrire(self) -> bool:
    """Vérifie si l'inscription est possible"""
    
    # 1. API chargée ?
    if not self.api_chargee_avec_succes:
        return False
        
    # 2. Identifiant disponible ?
    identifiant = self.config.get("identifiant") or self.environnement.get("identifiant")
    if not identifiant:
        return False
        
    # 3. Inscription activée ?
    if not self.config.get("inscription"):
        return False
        
    return True
```

## Structure des Erreurs d'Initialisation (status=3)

```json
{
  "identifiant": "SCENARIO_ID",
  "scenario": "nom_scenario",
  "date": "2025-01-15T14:30:00.000000",
  "duree": 0.052,
  "status": 3,
  "nb_scene": 0,
  "commentaire": "Erreur lors de l'initialisation du scénario - Scénario non lancé",
  "injecteur": "hostname-jenkins",
  "navigateur": "firefox",
  "interface_ip": "127.0.0.1",
  "status_initial": 3,
  "commentaire_initial": "Erreur lors de l'initialisation du scénario - Scénario non lancé",
  "briques": []
}
```

## Avantages de cette Approche

1. **Séquentiel et prévisible** : Chaque phase se déroule dans l'ordre
2. **Gestion d'erreurs claire** : Deux catégories avec règles précises
3. **Pas de classe supplémentaire** : Tout reste dans `Execution`
4. **Compatible avec pytest** : Fixture inchangée
5. **Logs structurés** : Chaque phase est identifiée
6. **Inscription appropriée** : Selon les règles métier

## Utilisation

```python
# Dans pytest ou directement
try:
    execution = Execution()  # Toute l'initialisation se fait ici
    # Si on arrive ici, tout est OK pour lancer les tests
    
except SystemExit as e:
    # Gestion automatique des erreurs avec les bons codes de sortie
    # et inscriptions API appropriées
    pass
```

## Migration depuis l'Ancienne Version

1. **Aucun changement** dans les fixtures pytest
2. **Aucun changement** dans les tests existants
3. **Aucun changement** dans `etape.py`, `contexte.py`, etc.
4. **Seul `execution.py`** est modifié avec la logique séquentielle
5. **Gestion d'erreurs** automatique avec codes de sortie appropriés

## Cas Particuliers d'Inscription

### 🚫 Cas où l'inscription n'est JAMAIS possible

1. **Variables d'environnement manquantes** (phase 1)
2. **Échec chargement API** (phase 2)
3. **Planning non respecté** (phase 3)
4. **Identifiant scénario manquant** (même après phase 2)

### ⚠️ Cas où l'inscription est tentée mais peut échouer

```python
# Exemple de logs selon les cas :

# Cas 1: API non chargée
"⚠️ API non chargée - Pas d'inscription"

# Cas 2: Identifiant manquant
"⚠️ Identifiant scénario non disponible - Pas d'inscription"
"ℹ️ Pas d'inscription API (identifiant scénario manquant)"

# Cas 3: Inscription désactivée
"⚠️ Inscription désactivée"

# Cas 4: Succès inscription
"✅ Erreur d'initialisation inscrite"
"✅ Erreur d'initialisation inscrite en base"

# Cas 5: Échec inscription
"❌ Échec inscription: ConnectionError..."
"📄 Données d'erreur:" + JSON dump
```

### 🔧 Points de Contrôle

| Étape | Vérification | Action si échec |
|-------|-------------|----------------|
| Phase 2 | API accessible ? | ErreurPreExecution |
| Phase 4+ | API chargée ? | Pas d'inscription |
| Phase 4+ | Identifiant présent ? | Pas d'inscription |
| Phase 4+ | Inscription activée ? | Pas d'inscription |
| Inscription | Connexion API OK ? | Dump JSON local |

Cette approche garantit qu'aucune donnée incomplète ou non autorisée ne sera envoyée à l'API d'inscription.
