## Questions de clarification :

### 1. **Sur la séparation des responsabilités**

- Dans `run_scenario.py`, je vois plusieurs types de logiques mélangées :
  - Configuration/environnement (`init_var_env`)
  - API calls (`get_scenario_last_execution`, `post_execution_result_in_isac`)
  - Exécution de tests (`run_generated_test`, `run_yaml_test`, `run_exadata_test`)
  - Orchestration (`run_scenario`, `run_multi_scenarios`)
  
  Voulez-vous que je sépare ces responsabilités dans des fichiers distincts (par exemple : `config.py`, `api_client.py`, `test_runners.py`, `orchestrator.py`) ? Oui pour que ce soit plus clair

### 2. **Sur les redondances**

- Je remarque que les variables d’environnement sont lues plusieurs fois à différents endroits
- Les appels API suivent des patterns similaires avec gestion d’erreurs répétée
- Souhaitez-vous une classe ou un module centralisé pour gérer :
  - Les variables d’environnement ? OUi mais comment cela sera utilisé après ?
  - Les appels API avec leur gestion d’erreurs ? Oui

### 3. **Sur la cohérence**

- J’observe des incohérences dans la gestion des types :
  - Parfois `env_vars['lecture']` est un booléen, parfois on compare avec `'true'` (string)
  - `url_api` est passé en paramètre mais aussi accessible via `env_vars`
  
  Voulez-vous standardiser cela avec une classe de configuration typée ? En fait, quand la variable lecture est récupérée via la variable d'environnement LECTURE c'est un str mais je veux la transformé en Booléen pour faciliter son utilisation par la suite (pareil pour les autres booléen). `url_api` est une variable d'environnement que je rècupère et que je veux pouvoir utiliser par la suite.

### 4. **Sur la maintenabilité**

- Les fonctions `check_env_variable` dans `helpers.py` et `init_var_env` dans `run_scenario.py` semblent avoir des responsabilités qui se chevauchent
- Préférez-vous :
  - Une classe `EnvironmentConfig` qui gère tout ? je ne veux pas créer de classe mais je veux avoir des fonctions qui sont cohérentes
  - Garder la séparation mais mieux définir les rôles ? Fais le plus simple et le plus modulaire

### 5. **Sur l’architecture générale**

Quelle structure vous semble la plus appropriée ?

**Option A - Modulaire par domaine :**

```
cli/
  ├── config/          # Gestion configuration & env
  ├── api/             # Client API
  ├── runners/         # Exécuteurs de tests
  ├── display/         # Affichage Rich (helpers actuels)
  └── orchestrator.py  # Logique principale
```

**Option B - Par couche :**

```
cli/
  ├── core/            # Logique métier
  ├── services/        # Services (API, config)
  ├── ui/              # Interface (Rich)
  └── commands/        # Points d'entrée CLI
```

Option B.

### 6. **Questions spécifiques**

- La fonction `show_env_config_help()` affiche un tableau avec des valeurs par défaut. Ces valeurs devraient-elles être centralisées quelque part pour éviter la duplication avec `init_var_env()` ? Oui certainement
- Les chemins de fichiers (YAML, config, rapports) sont construits à plusieurs endroits. Voulez-vous un module `paths.py` centralisé ? Oui 

Pouvez-vous me préciser vos préférences sur ces points pour que je propose une refactorisation adaptée à vos besoins ?​​​​​​​​​​​​​​​​

En fait, mes objectifs sont les suivants :
- Permettre l'affichage des erreurs avec les bons messages et une interface propre et simple pour les utilisateurs
- Vérifier que les variables requises sont bien définies et si ce n'est pas le cas empêcher le lancement d'une exécution alors qu'on s'est déjà qu'elle va s'arrêter
- Définier les valeurs par défauts des variables d'envrionnement car les variables d'envrionnement sont appelées par la suite dans les scénarios
- Avoir un code modulaire mais simple avec des fonctions très basiques et compréhensibles par d'autres développeurs (ne pas faire des fonctions complexes)
