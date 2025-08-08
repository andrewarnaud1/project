Les outils de génération de diagrammes de classes ont des capacités différentes pour montrer l'**utilisation** versus les **relations structurelles**. Voici les distinctions importantes :

## Ce que montrent les diagrammes de classes classiques

**Pyreverse** et la plupart des générateurs de diagrammes UML montrent principalement :
- ✅ **Relations structurelles** : héritage, composition, agrégation
- ✅ **Définitions** : classes, méthodes, attributs
- ❌ **Appels/utilisations** : qui appelle quoi, où une classe est instanciée

## Pour voir les utilisations et appels

Vous avez besoin d'outils différents :

### 1. Diagrammes de flux d'appels avec pycallgraph### 2. Autres outils spécialisés pour l'analyse d'usage

```bash
# Pour les appels dynamiques
pip install pycallgraph2
pycallgraph graphviz --output-file=usage.png -- python votre_script.py

# Pour l'analyse statique avancée
pip install vulture  # Trouve le code mort
vulture votre_dossier/

# Analyse de dépendances
pip install pydeps
pydeps votre_module --show-deps
```

### 3. Script pour combiner diagramme de classes + analyse d'usage## Résumé des capacités

**Pour voir les UTILISATIONS (qui utilise quoi) :**
- ✅ **Analyse statique** : Mon script `usage_analyzer.py` 
- ✅ **Graphiques d'appels** : `pycallgraph` (analyse dynamique)
- ✅ **Code mort** : `vulture` (trouve ce qui n'est jamais utilisé)

**Pour voir la STRUCTURE (classes, méthodes, héritage) :**
- ✅ **Diagrammes UML** : `pyreverse`, `py2puml`

**Usage recommandé :**
```bash
# Installation complète
pip install pylint pycallgraph2 vulture

# Analyse complète
python complete_analysis.py /votre/projet MonApp
```

Cela vous donnera :
- Diagramme de classes structurel
- Rapport détaillé des utilisations
- Classes potentiellement inutilisées  
- Graphique des appels (si possible)
- Rapport HTML navigable

La différence clé est que les **diagrammes de classes** montrent la structure, tandis que l'**analyse d'usage** montre les dépendances réelles dans votre code.
