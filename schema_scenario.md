```mermaid

flowchart TD
%% === PHASE 1: INITIALISATION ===
Start([DÉBUT EXÉCUTION SCÉNARIO]) --> InitEnv[Chargement variables d’environnement SCENARIO, LECTURE, BROWSER, etc.]

%% Validation variable SCENARIO (obligatoire)
InitEnv --> CheckScenario{Variable SCENARIO définie ?}
CheckScenario -->|NON| ExitScenarioKO[❌ ARRÊT FATAL EXIT CODE 2 Variable SCENARIO manquante]
CheckScenario -->|OUI| ValidScenario[✅ SCENARIO = {nom_scenario}]

%% === PHASE 2: MODE D'EXÉCUTION ===
ValidScenario --> CheckLecture{Variable LECTURE ?}
CheckLecture -->|FALSE| CheckEnvDev{Environnement développement ?}
CheckLecture -->|TRUE| InitAPIMode[🌐 Mode API activé]

%% Branche développement sans API
CheckEnvDev -->|OUI| DevMode[💻 Mode développement Sans vérifications API]
CheckEnvDev -->|NON| ExitProdNoAPI[❌ ARRÊT PROD EXIT CODE 2 API obligatoire en production]

%% === PHASE 3: CONFIGURATION ===
DevMode --> LoadConfigDev[📖 Chargement configuration fichier local uniquement]
InitAPIMode --> CallAPI[🔗 Appel API scénario]

%% Gestion erreur API
CallAPI --> APIResult{Réponse API valide ?}
APIResult -->|NON| HandleAPIError[⚠️ Gestion erreur API Inscription status UNKNOWN]
APIResult -->|OUI| ValidateAPIData[✅ Données API récupérées]

HandleAPIError --> SaveFailureReport[💾 Sauvegarde rapport échec Type: Infrastructure]
SaveFailureReport --> ExitAPIError[❌ ARRÊT EXIT CODE 3 Erreur infrastructure]

%% === PHASE 4: VÉRIFICATIONS MÉTIER ===
ValidateAPIData --> CheckScenarioActive{Scénario actif dans l'API ?}
CheckScenarioActive -->|NON| LogInactive[📝 Log: Scénario désactivé]
CheckScenarioActive -->|OUI| CheckSchedule[📅 Vérification planning]

LogInactive --> ExitInactive[🔄 ARRÊT NORMAL EXIT CODE 0 Scénario inactif]

%% Vérification planning (jour férié + horaires)
CheckSchedule --> IsHoliday{Jour férié ?}
IsHoliday -->|OUI| CheckHolidayFlag{flag_ferie = true ?}
IsHoliday -->|NON| CheckTimeSlots[⏰ Vérification créneaux horaires]

CheckHolidayFlag -->|NON| ExitHoliday[🚫 ARRÊT PLANNING EXIT CODE 2 Interdit jours fériés]
CheckHolidayFlag -->|OUI| CheckTimeSlots

CheckTimeSlots --> HasValidSlot{Créneau valide trouvé ?}
HasValidSlot -->|NON| ExitTimeSlot[⏰ ARRÊT PLANNING EXIT CODE 2 Hors créneaux autorisés]
HasValidSlot -->|OUI| ScheduleOK[✅ Planning respecté]

%% === PHASE 5: CONFIGURATION COMPLÈTE ===
LoadConfigDev --> MergeConfig[🔧 Fusion configuration]
ScheduleOK --> LoadConfigProd[📖 Chargement config complète API + fichiers locaux]
LoadConfigProd --> MergeConfig

MergeConfig --> CreateDirectories[📁 Création répertoires screenshots, rapports]
CreateDirectories --> InitBrowserConfig[🌐 Configuration navigateur proxy, cookies, options]

%% === PHASE 6: LANCEMENT NAVIGATEUR ===
InitBrowserConfig --> LaunchBrowser[🔌 Lancement Playwright Browser + Context]
LaunchBrowser --> BrowserOK{Navigateur démarré ?}
BrowserOK -->|NON| HandleBrowserError[⚠️ Erreur navigateur]
BrowserOK -->|OUI| CreatePage[📄 Création première page]

HandleBrowserError --> SaveBrowserFailure[💾 Sauvegarde erreur navigateur]
SaveBrowserFailure --> ExitBrowserError[❌ ARRÊT EXIT CODE 2 Erreur navigateur]

%% === PHASE 7: EXÉCUTION TESTS ===
CreatePage --> StartTracing[📹 Démarrage traces réseau]
StartTracing --> RunTests[🎯 EXÉCUTION TESTS Étapes du scénario]

RunTests --> TestsResult{Résultat tests ?}
TestsResult -->|SUCCÈS| TestsSuccess[✅ Tous tests OK]
TestsResult -->|ÉCHEC| TestsFailure[❌ Tests en échec]
TestsResult -->|TIMEOUT| TestsTimeout[⏰ Timeout détecté]

%% === PHASE 8: FINALISATION ===
TestsSuccess --> FinalizeSuccess[📊 Finalisation succès Status: SUCCESS]
TestsFailure --> FinalizeFailure[📊 Finalisation échec Status: FAILURE]
TestsTimeout --> FinalizeTimeout[📊 Finalisation timeout Status: TIMEOUT]

FinalizeSuccess --> GenerateReport[📋 Génération rapport JSON]
FinalizeFailure --> GenerateReport
FinalizeTimeout --> GenerateReport

GenerateReport --> StopTracing[📹 Arrêt traces et captures]
StopTracing --> CloseBrowser[🔌 Fermeture navigateur]

%% === PHASE 9: INSCRIPTION RÉSULTATS ===
CloseBrowser --> CheckInscription{Inscription API activée ?}
CheckInscription -->|NON| LocalSave[💾 Sauvegarde locale uniquement]
CheckInscription -->|OUI| SendToAPI[📤 Envoi résultats à l'API]

SendToAPI --> APISendResult{Envoi réussi ?}
APISendResult -->|NON| APISendError[⚠️ Erreur envoi API Sauvegarde locale]
APISendResult -->|OUI| APISendOK[✅ Résultats inscrits]

LocalSave --> FinalSuccess[🎯 FIN SUCCÈS EXIT CODE 0]
APISendError --> FinalSuccess
APISendOK --> FinalSuccess

%% === STYLES ===
classDef successClass fill:#d4edda,stroke:#28a745,stroke-width:2px,color:#155724
classDef errorClass fill:#f8d7da,stroke:#dc3545,stroke-width:2px,color:#721c24
classDef warningClass fill:#fff3cd,stroke:#ffc107,stroke-width:2px,color:#856404
classDef processClass fill:#e2e3e5,stroke:#6c757d,stroke-width:2px,color:#495057
classDef decisionClass fill:#cce5ff,stroke:#007bff,stroke-width:2px,color:#004085
classDef infoClass fill:#e7f3ff,stroke:#17a2b8,stroke-width:2px,color:#0c5460

%% Application des styles
class Start,InitEnv,LoadConfigDev,LoadConfigProd,MergeConfig,CreateDirectories,InitBrowserConfig,LaunchBrowser,CreatePage,StartTracing,GenerateReport,StopTracing,CloseBrowser processClass
class CheckScenario,CheckLecture,CheckEnvDev,APIResult,CheckScenarioActive,IsHoliday,CheckHolidayFlag,HasValidSlot,BrowserOK,TestsResult,CheckInscription,APISendResult decisionClass
class ValidScenario,InitAPIMode,ValidateAPIData,ScheduleOK,TestsSuccess,FinalizeSuccess,APISendOK,LocalSave,FinalSuccess successClass
class ExitScenarioKO,ExitProdNoAPI,ExitAPIError,ExitInactive,ExitHoliday,ExitTimeSlot,ExitBrowserError,TestsFailure,TestsTimeout,FinalizeFailure,FinalizeTimeout,APISendError errorClass
class DevMode,HandleAPIError,LogInactive,CheckSchedule,CheckTimeSlots,HandleBrowserError,SaveFailureReport,SaveBrowserFailure,APISendError warningClass
class CallAPI,RunTests,SendToAPI infoClass
```
