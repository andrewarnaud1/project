```mermaid
flowchart TD
%% === PHASE 1: INITIALISATION ===
Start([DEBUT EXECUTION SCENARIO]) –> InitEnv[Chargement variables environnement SCENARIO, LECTURE, BROWSER, etc.]

%% Validation variable SCENARIO (obligatoire)
InitEnv --> CheckScenario{Variable SCENARIO definie ?}
CheckScenario -->|NON| ExitScenarioKO[ARRET FATAL - EXIT CODE 2 - Variable SCENARIO manquante]
CheckScenario -->|OUI| ValidScenario[SCENARIO valide]

%% === PHASE 2: MODE D'EXECUTION ===
ValidScenario --> CheckLecture{Variable LECTURE ?}
CheckLecture -->|FALSE| CheckEnvDev{Environnement developpement ?}
CheckLecture -->|TRUE| InitAPIMode[Mode API active]

%% Branche développement sans API
CheckEnvDev -->|OUI| DevMode[Mode developpement - Sans verifications API]
CheckEnvDev -->|NON| ExitProdNoAPI[ARRET PROD - EXIT CODE 2 - API obligatoire en production]

%% === PHASE 3: CONFIGURATION ===
DevMode --> LoadConfigDev[Chargement configuration - fichier local uniquement]
InitAPIMode --> CallAPI[Appel API scenario]

%% Gestion erreur API
CallAPI --> APIResult{Reponse API valide ?}
APIResult -->|NON| ExitAPIError[ARRET FATAL - EXIT CODE 3 - Erreur infrastructure API]
APIResult -->|OUI| ValidateAPIData[Donnees API recuperees]

%% === PHASE 4: VERIFICATIONS METIER ===
ValidateAPIData --> CheckScenarioActive{Scenario actif dans API ?}
CheckScenarioActive -->|NON| ExitInactive[ARRET NORMAL - EXIT CODE 0 - Scenario desactive]
CheckScenarioActive -->|OUI| CheckSchedule[Verification planning]

%% Vérification planning (jour férié + horaires)
CheckSchedule --> IsHoliday{Jour ferie ?}
IsHoliday -->|OUI| CheckHolidayFlag{flag_ferie = true ?}
IsHoliday -->|NON| CheckTimeSlots[Verification creneaux horaires]

CheckHolidayFlag -->|NON| ExitHoliday[ARRET NORMAL - EXIT CODE 0 - Interdit jours feries]
CheckHolidayFlag -->|OUI| CheckTimeSlots

CheckTimeSlots --> HasValidSlot{Creneau valide trouve ?}
HasValidSlot -->|NON| ExitTimeSlot[ARRET NORMAL - EXIT CODE 0 - Hors creneaux autorises]
HasValidSlot -->|OUI| ScheduleOK[Planning respecte - DEBUT EXECUTION REELLE]

%% === PHASE 5: CONFIGURATION COMPLETE ===
LoadConfigDev --> MergeConfig[Fusion configuration]
ScheduleOK --> LoadConfigProd[Chargement config complete - API + fichiers locaux]
LoadConfigProd --> MergeConfig

MergeConfig --> CreateDirectories[Creation repertoires - screenshots, rapports]
CreateDirectories --> InitBrowserConfig[Configuration navigateur - proxy, cookies, options]

%% === PHASE 6: LANCEMENT NAVIGATEUR ===
InitBrowserConfig --> LaunchBrowser[Lancement Playwright - Browser + Context]
LaunchBrowser --> BrowserOK{Navigateur demarre ?}
BrowserOK -->|NON| SaveBrowserFailure[Sauvegarde rapport echec navigateur - Status: FAILURE]
BrowserOK -->|OUI| CreatePage[Creation premiere page]

SaveBrowserFailure --> SendBrowserFailure[Inscription echec navigateur]
SendBrowserFailure --> ExitBrowserError[ARRET - EXIT CODE 2 - Erreur navigateur]

%% === PHASE 7: EXECUTION TESTS ===
CreatePage --> StartTracing[Demarrage traces reseau]
StartTracing --> RunTests[EXECUTION TESTS - Etapes du scenario]

RunTests --> TestsResult{Resultat tests ?}
TestsResult -->|SUCCES| TestsSuccess[Tous tests OK]
TestsResult -->|ECHEC| TestsFailure[Tests en echec]
TestsResult -->|TIMEOUT| TestsTimeout[Timeout detecte]

%% === PHASE 8: FINALISATION ===
TestsSuccess --> FinalizeSuccess[Finalisation succes - Status: SUCCESS]
TestsFailure --> FinalizeFailure[Finalisation echec - Status: FAILURE]
TestsTimeout --> FinalizeTimeout[Finalisation timeout - Status: TIMEOUT]

FinalizeSuccess --> GenerateReport[Generation rapport JSON]
FinalizeFailure --> GenerateReport
FinalizeTimeout --> GenerateReport

GenerateReport --> StopTracing[Arret traces et captures]
StopTracing --> CloseBrowser[Fermeture navigateur]

%% === PHASE 9: INSCRIPTION RESULTATS ===
CloseBrowser --> CheckInscription{Inscription API activee ?}
CheckInscription -->|NON| LocalSave[Sauvegarde locale uniquement]
CheckInscription -->|OUI| SendToAPI[Envoi resultats a API]

SendToAPI --> APISendResult{Envoi reussi ?}
APISendResult -->|NON| APISendError[Erreur envoi API - Sauvegarde locale]
APISendResult -->|OUI| APISendOK[Resultats inscrits]

LocalSave --> FinalSuccess[FIN SUCCES - EXIT CODE 0]
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
class ExitScenarioKO,ExitProdNoAPI,ExitAPIError,ExitBrowserError,TestsFailure,TestsTimeout,FinalizeFailure,FinalizeTimeout,APISendError errorClass
class DevMode,ExitInactive,ExitHoliday,ExitTimeSlot,SaveBrowserFailure,SendBrowserFailure warningClass
class CallAPI,RunTests,SendToAPI infoClass
```
