flowchart TD
%% =============================================================================
%% PHASE INITIALISATION
%% =============================================================================

```
START([🚀 Démarrage Simulateur]) --> LOAD_ENV[📁 EnvLoader.load_environment_variables]

LOAD_ENV --> CHECK_ENV{✅ Variables obligatoires présentes?}
CHECK_ENV -->|❌ Non| ERROR_ENV[❌ ValueError: Variables manquantes]
ERROR_ENV --> EXIT_1[🛑 pytest.exit(1)]

CHECK_ENV -->|✅ Oui| LOAD_YAML[📄 YamlLoader.load_scenario_config]
LOAD_YAML --> CHECK_YAML{✅ Fichier YAML valide?}
CHECK_YAML -->|❌ Non| ERROR_YAML[❌ FileNotFoundError: Config introuvable]
ERROR_YAML --> EXIT_1

CHECK_YAML -->|✅ Oui| LOAD_COMMON[📄 YamlLoader.load_common_config]
LOAD_COMMON --> MERGE_CONFIG[🔧 ConfigLoader.merge_configurations]

MERGE_CONFIG --> CHECK_API{🔌 API activée?}
CHECK_API -->|✅ Oui| API_CALL[🌐 ApiClient.load_scenario_data]

API_CALL --> CHECK_API_SUCCESS{✅ API accessible?}
CHECK_API_SUCCESS -->|❌ Non| ERROR_API[❌ ApiException: Échec appel API]
ERROR_API --> EXIT_1

CHECK_API_SUCCESS -->|✅ Oui| LOAD_PLANNING[📅 ApiClient.get_planning_data]
LOAD_PLANNING --> CHECK_PLANNING{⏰ Planning autorise exécution?}

CHECK_API -->|❌ Non| SKIP_API[⏭️ Configuration locale seulement]
SKIP_API --> CREATE_DIRS

CHECK_PLANNING -->|❌ Non| PLANNING_ERROR[❌ ScheduleError: Hors plage autorisée]
PLANNING_ERROR --> EXIT_1

CHECK_PLANNING -->|✅ Oui| MERGE_API[🔧 ConfigLoader.merge_api_data]
MERGE_API --> CREATE_DIRS[📁 FileUtils.create_directories]

CREATE_DIRS --> LOAD_USER[👤 UserManager.load_user_data]
LOAD_USER --> CHECK_CRYPTO{🔐 Données chiffrées?}
CHECK_CRYPTO -->|✅ Oui| DECRYPT[🔓 CryptoManager.decrypt_aes_gcm]
CHECK_CRYPTO -->|❌ Non| INIT_BROWSER
DECRYPT --> INIT_BROWSER[🌐 BrowserFactory.create_browser]

%% =============================================================================
%% PHASE LANCEMENT NAVIGATEUR
%% =============================================================================

INIT_BROWSER --> CHECK_BROWSER{🌐 Navigateur disponible?}
CHECK_BROWSER -->|❌ Non| ERROR_BROWSER[❌ PlaywrightError: Navigateur introuvable]
ERROR_BROWSER --> EXIT_2[🛑 pytest.exit(2)]

CHECK_BROWSER -->|✅ Oui| CREATE_CONTEXT[🎭 Browser.new_context]
CREATE_CONTEXT --> SET_PROXY{🔗 Proxy configuré?}
SET_PROXY -->|✅ Oui| APPLY_PROXY[🔗 Context.set_proxy]
SET_PROXY -->|❌ Non| SET_AUTH
APPLY_PROXY --> SET_AUTH{🔐 Auth HTTP?}
SET_AUTH -->|✅ Oui| APPLY_AUTH[🔐 Context.set_http_credentials]
SET_AUTH -->|❌ Non| CREATE_PAGE
APPLY_AUTH --> CREATE_PAGE[📄 Context.new_page]

CREATE_PAGE --> START_HAR{📊 HAR activé?}
START_HAR -->|✅ Oui| INIT_HAR[📊 Context.tracing.start]
START_HAR -->|❌ Non| CREATE_SCENARIO
INIT_HAR --> CREATE_SCENARIO[🎬 ScenarioBuilder.create_scenario]

%% =============================================================================
%% PHASE EXECUTION TESTS
%% =============================================================================

CREATE_SCENARIO --> PYTEST_DISCOVERY[🔍 pytest: Découverte tests]
PYTEST_DISCOVERY --> START_TEST[▶️ pytest: Lancement test_xxx]

START_TEST --> CREATE_STEP[📝 Scenario.create_step]
CREATE_STEP --> INC_COUNTER[🔢 Scenario.step_counter++]
INC_COUNTER --> INIT_STEP[📝 Step.__init__]

INIT_STEP --> EXEC_PLAYWRIGHT[🎭 Actions Playwright]
EXEC_PLAYWRIGHT --> CHECK_ACTION_TYPE{🎯 Type d'action?}

%% Actions Web Standard
CHECK_ACTION_TYPE -->|🌐 Web Standard| WEB_ACTION[🌐 page.get_by_role().click()]
WEB_ACTION --> CHECK_WEB_SUCCESS{✅ Action réussie?}

CHECK_WEB_SUCCESS -->|❌ Non| CATCH_EXCEPTION[⚠️ Exception capturée]
CATCH_EXCEPTION --> ANALYZE_ERROR[🔍 ErrorAnalyzer.classify_error]

ANALYZE_ERROR --> CHECK_TIMEOUT{⏰ Timeout?}
CHECK_TIMEOUT -->|✅ Oui| TIMEOUT_ANALYSIS[🔍 TimeoutChecker.analyze_cause]
CHECK_TIMEOUT -->|❌ Non| STANDARD_ERROR

TIMEOUT_ANALYSIS --> CHECK_APP_ERROR{🐛 Erreur applicative détectée?}
CHECK_APP_ERROR -->|✅ Oui| APP_ERROR[🐛 Erreur app: Code 500 détecté]
CHECK_APP_ERROR -->|❌ Non| TIMEOUT_ERROR[⏰ Timeout standard]

APP_ERROR --> SCREENSHOT_ERROR
TIMEOUT_ERROR --> SCREENSHOT_ERROR
STANDARD_ERROR[❌ Erreur standard] --> SCREENSHOT_ERROR[📸 Step.take_screenshot(error=True)]

SCREENSHOT_ERROR --> STEP_ERROR[❌ Step.error()]
STEP_ERROR --> FINALIZE_STEP[🏁 Step._finalize()]
FINALIZE_STEP --> EXIT_2

%% Actions Exadata
CHECK_ACTION_TYPE -->|🖼️ Exadata| EXADATA_ACTION[🖼️ ExadataActions.click_image]
EXADATA_ACTION --> TAKE_SCREENSHOT_ANALYSIS[📸 VisionEngine.take_screenshot]
TAKE_SCREENSHOT_ANALYSIS --> FIND_IMAGE[🔍 VisionEngine.find_image_coordinates]
FIND_IMAGE --> CHECK_FOUND{✅ Image trouvée?}
CHECK_FOUND -->|❌ Non| CHECK_RETRY{🔄 Retry disponible?}
CHECK_RETRY -->|✅ Oui| RETRY_LOWER_CONFIDENCE[🔄 Retry avec confiance réduite]
RETRY_LOWER_CONFIDENCE --> FIND_IMAGE
CHECK_RETRY -->|❌ Non| EXADATA_ERROR[❌ Image non trouvée]
EXADATA_ERROR --> SCREENSHOT_ERROR

CHECK_FOUND -->|✅ Oui| CLICK_COORDINATES[🖱️ Page.mouse.click(x, y)]
CLICK_COORDINATES --> CHECK_WEB_SUCCESS

%% Succès des actions
CHECK_WEB_SUCCESS -->|✅ Oui| CHECK_SCREENSHOT{📸 Screenshot demandé?}
CHECK_SCREENSHOT -->|✅ Oui| TAKE_SCREENSHOT[📸 Step.take_screenshot()]
CHECK_SCREENSHOT -->|❌ Non| MORE_ACTIONS

TAKE_SCREENSHOT --> INC_SCREENSHOT[🔢 Step._screenshot_counter++]
INC_SCREENSHOT --> GENERATE_FILENAME[📝 Générer nom: XX_YY_nom.png]
GENERATE_FILENAME --> ADD_ANNOTATIONS[🖼️ ScreenshotManager.add_annotations]
ADD_ANNOTATIONS --> CAPTURE_IMAGE[📸 Page.screenshot()]
CAPTURE_IMAGE --> CLEANUP_ANNOTATIONS[🧹 ScreenshotManager.cleanup]
CLEANUP_ANNOTATIONS --> MORE_ACTIONS{🔄 Autres actions dans le test?}

MORE_ACTIONS -->|✅ Oui| EXEC_PLAYWRIGHT
MORE_ACTIONS -->|❌ Non| STEP_SUCCESS[✅ Step.success()]

STEP_SUCCESS --> CALC_DURATION[⏱️ Calculer durée étape]
CALC_DURATION --> ADD_TO_COMPLETED[📋 Scenario.add_completed_step()]
ADD_TO_COMPLETED --> CHECK_MORE_TESTS{🔄 Autres tests à exécuter?}

%% =============================================================================
%% PHASE FINALISATION
%% =============================================================================

CHECK_MORE_TESTS -->|✅ Oui| START_TEST
CHECK_MORE_TESTS -->|❌ Non| FINALIZE_SCENARIO[🏁 Scenario.finalize()]

FINALIZE_SCENARIO --> CALC_TOTAL_DURATION[⏱️ Calculer durée totale]
CALC_TOTAL_DURATION --> DETERMINE_STATUS[📊 Déterminer statut global]
DETERMINE_STATUS --> GENERATE_REPORT[📄 Reporter.generate_json_report]

GENERATE_REPORT --> SAVE_LOCAL[💾 Sauvegarder rapport local]
SAVE_LOCAL --> CHECK_API_ENABLED{🔌 Inscription API activée?}

CHECK_API_ENABLED -->|❌ Non| STOP_HAR
CHECK_API_ENABLED -->|✅ Oui| SEND_API[🌐 ApiClient.save_execution_results]

SEND_API --> CHECK_API_SEND{✅ Envoi API réussi?}
CHECK_API_SEND -->|❌ Non| LOG_API_ERROR[📝 Log: Échec envoi API]
CHECK_API_SEND -->|✅ Oui| LOG_API_SUCCESS[📝 Log: Envoi API réussi]

LOG_API_ERROR --> STOP_HAR
LOG_API_SUCCESS --> STOP_HAR{📊 HAR activé?}

STOP_HAR -->|✅ Oui| SAVE_HAR[📊 Context.tracing.stop()]
STOP_HAR -->|❌ Non| CLEANUP_BROWSER
SAVE_HAR --> CLEANUP_BROWSER[🧹 Browser.close()]

CLEANUP_BROWSER --> SUCCESS_END[✅ Fin d'exécution réussie]

%% =============================================================================
%% GESTION DES CAS SPECIAUX
%% =============================================================================

%% Gestion des iFrames
EXEC_PLAYWRIGHT -.-> CHECK_IFRAME{🖼️ iFrame?}
CHECK_IFRAME -->|✅ Oui| LOCATE_IFRAME[🔍 Page.frame_locator()]
LOCATE_IFRAME --> WAIT_IFRAME[⏳ Frame.wait_for_load_state()]
WAIT_IFRAME --> IFRAME_ACTION[🎭 Actions dans iFrame]
IFRAME_ACTION --> CHECK_WEB_SUCCESS
CHECK_IFRAME -->|❌ Non| WEB_ACTION

%% Gestion WebActions (optionnel)
WEB_ACTION -.-> USE_WEBACTIONS{🔧 WebActions utilisé?}
USE_WEBACTIONS -->|✅ Oui| WEBACTIONS_TRY[🛡️ WebActions.try_action()]
WEBACTIONS_TRY --> WEBACTIONS_EXPECT[⏳ expect().to_be_visible()]
WEBACTIONS_EXPECT --> WEBACTIONS_ACTION[🎯 Exécuter action]
WEBACTIONS_ACTION --> WEBACTIONS_CATCH[🛡️ Catch automatique]
WEBACTIONS_CATCH --> CHECK_WEB_SUCCESS
USE_WEBACTIONS -->|❌ Non| WEB_ACTION

%% Gestion relance automatique
CHECK_PLANNING -.-> CHECK_RELANCE{🔄 Relance activée?}
CHECK_RELANCE -->|✅ Oui| CHECK_LAST_EXEC[📊 ApiClient.get_last_execution()]
CHECK_LAST_EXEC --> LAST_EXEC_STATUS{📊 Dernier statut?}
LAST_EXEC_STATUS -->|✅ Succès| SKIP_EXECUTION[⏭️ Skip: Pas de relance nécessaire]
LAST_EXEC_STATUS -->|❌ Échec| CONTINUE_EXECUTION[▶️ Continuer: Relance nécessaire]
SKIP_EXECUTION --> EXIT_1
CONTINUE_EXECUTION --> MERGE_API
CHECK_RELANCE -->|❌ Non| MERGE_API

%% Gestion rotation des données
LOAD_USER -.-> CHECK_ROTATION{🔄 Rotation données?}
CHECK_ROTATION -->|✅ Oui| READ_CACHE[📁 Lire fichier cache rotation]
READ_CACHE --> GET_ROTATION_DATA[📊 get_conf_data_from_scenario()]
GET_ROTATION_DATA --> UPDATE_CACHE[📁 Mettre à jour cache]
UPDATE_CACHE --> INIT_BROWSER
CHECK_ROTATION -->|❌ Non| INIT_BROWSER

%% =============================================================================
%% STYLES
%% =============================================================================

classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:3px
classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px
classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
classDef success fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
classDef api fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
classDef screenshot fill:#fff8e1,stroke:#f57f17,stroke-width:2px

class START,SUCCESS_END startEnd
class LOAD_ENV,LOAD_YAML,MERGE_CONFIG,CREATE_DIRS,INIT_BROWSER,CREATE_STEP process
class CHECK_ENV,CHECK_YAML,CHECK_API,CHECK_PLANNING,CHECK_BROWSER,CHECK_ACTION_TYPE decision
class ERROR_ENV,ERROR_YAML,ERROR_API,ERROR_BROWSER,SCREENSHOT_ERROR,STEP_ERROR error
class STEP_SUCCESS,LOG_API_SUCCESS success
class API_CALL,SEND_API,CHECK_API_SEND api
class TAKE_SCREENSHOT,ADD_ANNOTATIONS,CAPTURE_IMAGE screenshot
```