```mermaid

flowchart TD
Start([🚀 DEBUT EXECUTION SCENARIO]) –> LoadEnv[📋 Chargement Variables d’Environnement]

%% Validation variables environnement
LoadEnv --> ValidateEnv{Variables obligatoires<br/>presentes ?}
ValidateEnv -->|NON| ErrorEnv[❌ ERREUR<br/>Variables manquantes<br/>EXIT CODE 2]

%% Chargement configuration fichier
ValidateEnv -->|OUI| LoadConfig[📄 Chargement Configuration<br/>Fichier YAML]
LoadConfig --> ValidateConfig{Fichier configuration<br/>valide ?}
ValidateConfig -->|NON| ErrorConfig[❌ ERREUR<br/>Configuration invalide<br/>EXIT CODE 2]

%% Verification mode lecture API
ValidateConfig -->|OUI| CheckLectureMode{LECTURE = true ?}

%% Mode hors ligne (LECTURE=false)
CheckLectureMode -->|NON| OfflineMode[📴 Mode Hors Ligne<br/>Configuration fichier uniquement]
OfflineMode --> CreateDirs1[📁 Creation Repertoires Sortie]

%% Mode en ligne (LECTURE=true)
CheckLectureMode -->|OUI| CallAPI[🌐 Appel API Scenario]
CallAPI --> APISuccess{API accessible<br/>et donnees valides ?}

%% Erreur API
APISuccess -->|NON| HandleAPIError[⚠️ Gestion Erreur API]
HandleAPIError --> SaveUnknownStatus[💾 Sauvegarde Status UNKNOWN<br/>Type: Infrastructure]
SaveUnknownStatus --> ErrorAPI[❌ ARRÊT<br/>Erreur Infrastructure<br/>EXIT CODE 3]

%% Succès API - Verification planning
APISuccess -->|OUI| MergeConfig[🔄 Fusion Configuration<br/>API + Fichier + Environnement]
MergeConfig --> CheckScheduling{Verification<br/>Planning d'Execution}

%% Verification jours feries
CheckScheduling --> IsHoliday{Jour ferie ?}
IsHoliday -->|OUI| CheckHolidayFlag{flag_ferie = true ?}
CheckHolidayFlag -->|NON| ErrorHoliday[❌ ARRÊT<br/>Execution interdite<br/>les jours feries<br/>EXIT CODE 2]

%% Verification plages horaires
IsHoliday -->|NON| CheckTimeSlots[⏰ Verification Plages Horaires]
CheckHolidayFlag -->|OUI| CheckTimeSlots

CheckTimeSlots --> InTimeSlot{Heure dans<br/>plage autorisee ?}
InTimeSlot -->|NON| ErrorTimeSlot[❌ ARRÊT<br/>Heure hors planning<br/>EXIT CODE 2]

%% Creation environnement d'execution
InTimeSlot -->|OUI| CreateDirs2[📁 Creation Repertoires Sortie]
CreateDirs1 --> LoadUsers
CreateDirs2 --> LoadUsers[👤 Chargement Utilisateurs ISAC]

LoadUsers --> ValidateUsers{Utilisateurs<br/>valides ?}
ValidateUsers -->|NON| ErrorUsers[❌ ERREUR<br/>Utilisateurs invalides<br/>EXIT CODE 2]

%% Lancement navigateur
ValidateUsers -->|OUI| LaunchBrowser[🌐 Lancement Navigateur Playwright]
LaunchBrowser --> BrowserSuccess{Navigateur<br/>lance avec succès ?}

BrowserSuccess -->|NON| ErrorBrowser[❌ ERREUR<br/>Echec lancement navigateur<br/>EXIT CODE 2]

%% Creation contexte et page
BrowserSuccess -->|OUI| CreateContext[🖥️ Creation Contexte Navigateur<br/>+ Configuration Proxy/Cookies]
CreateContext --> CreatePage[📄 Creation Page Initiale]
CreatePage --> StartTracing[📹 Demarrage Enregistrement Traces]

%% Execution des etapes
StartTracing --> InitExecution[⚙️ Initialisation Execution<br/>Compteur etapes = 0]
InitExecution --> ExecuteSteps[🔄 Boucle d'Execution des Etapes]

%% Traitement d'une etape
ExecuteSteps --> NextStep{Etape suivante<br/>disponible ?}
NextStep -->|NON| AllStepsComplete[✅ Toutes les Etapes Terminees]

NextStep -->|OUI| IncrementCounter[📊 Increment Compteur Etapes]
IncrementCounter --> ExecuteStep[⚡ Execution Etape Courante]

%% Resultat d'une etape
ExecuteStep --> StepResult{Resultat<br/>etape ?}

%% Etape en succès
StepResult -->|SUCCÈS| StepSuccess[✅ Etape Reussie<br/>Status = 0]
StepSuccess --> TakeScreenshot1[📸 Capture d'Ecran Success]
TakeScreenshot1 --> LogStepSuccess[📝 Log Etape OK]
LogStepSuccess --> SaveStepResult1[💾 Sauvegarde Resultat Etape]
SaveStepResult1 --> ExecuteSteps

%% Etape en avertissement
StepResult -->|AVERTISSEMENT| StepWarning[⚠️ Etape avec Avertissement<br/>Status = 1]
StepWarning --> TakeScreenshot2[📸 Capture d'Ecran Warning]
TakeScreenshot2 --> LogStepWarning[📝 Log Etape Warning]
LogStepWarning --> SaveStepResult2[💾 Sauvegarde Resultat Etape]
SaveStepResult2 --> ExecuteSteps

%% Etape en echec
StepResult -->|ECHEC| StepFailure[❌ Etape en Echec<br/>Status = 2]
StepFailure --> AnalyzeError[🔍 Analyse de l'Erreur]

%% Types d'erreurs
AnalyzeError --> ErrorType{Type d'erreur ?}

%% Timeout avec verification erreur applicative
ErrorType -->|TIMEOUT| CheckAppError[🔍 Verification Erreur Applicative<br/>dans la page HTML]
CheckAppError --> AppErrorFound{Erreur applicative<br/>detectee ?}
AppErrorFound -->|OUI| LogAppError[📝 Log: Timeout dû a erreur applicative]
AppErrorFound -->|NON| LogTimeout[📝 Log: Timeout standard]
LogAppError --> TakeErrorScreenshot
LogTimeout --> TakeErrorScreenshot

%% Autres erreurs
ErrorType -->|NAVIGATION| LogNavError[📝 Log: Erreur de navigation]
ErrorType -->|ELEMENT| LogElementError[📝 Log: Element introuvable]
ErrorType -->|AUTRE| LogOtherError[📝 Log: Autre erreur]

LogNavError --> TakeErrorScreenshot[📸 Capture d'Ecran Erreur]
LogElementError --> TakeErrorScreenshot
LogOtherError --> TakeErrorScreenshot

TakeErrorScreenshot --> SaveStepError[💾 Sauvegarde Resultat Erreur<br/>Status = 2]
SaveStepError --> StopOnError[🛑 Arrêt Execution sur Erreur<br/>EXIT CODE 2]

%% Finalisation succès
AllStepsComplete --> CalculateResults[📊 Calcul Resultats Finaux<br/>Duree, Statut Global, Stats]
CalculateResults --> StopTracing[📹 Arrêt Enregistrement Traces]
StopTracing --> SaveTraces[💾 Sauvegarde Traces Reseau<br/>network_trace.zip]

SaveTraces --> GenerateReports[📋 Generation Rapports]
GenerateReports --> SaveJSON[💾 Sauvegarde Rapport JSON<br/>scenario.json]

%% Inscription API (si activee)
SaveJSON --> CheckInscription{INSCRIPTION = true ?}
CheckInscription -->|NON| LogNoInscription[📝 Log: Resultats non inscrits]
CheckInscription -->|OUI| SendToAPI[🌐 Envoi Resultats vers API]

SendToAPI --> APIInscriptionSuccess{Inscription API<br/>reussie ?}
APIInscriptionSuccess -->|NON| LogAPIError[📝 Log: Erreur inscription API<br/>Mais continue...]
APIInscriptionSuccess -->|OUI| LogAPISuccess[📝 Log: Inscription API OK]

%% Nettoyage final
LogNoInscription --> CleanupResources[🧹 Nettoyage Ressources]
LogAPIError --> CleanupResources
LogAPISuccess --> CleanupResources

CleanupResources --> CloseBrowser[🔒 Fermeture Navigateur]
CloseBrowser --> FinalSuccess[🎯 SUCCÈS COMPLET<br/>EXIT CODE 0]

%% Styling des noeuds
classDef successClass fill:#d4edda,stroke:#28a745,stroke-width:2px,color:#155724
classDef errorClass fill:#f8d7da,stroke:#dc3545,stroke-width:2px,color:#721c24
classDef warningClass fill:#fff3cd,stroke:#ffc107,stroke-width:2px,color:#856404
classDef processClass fill:#e2e3e5,stroke:#6c757d,stroke-width:2px,color:#495057
classDef decisionClass fill:#cce5ff,stroke:#007bff,stroke-width:2px,color:#004085
classDef apiClass fill:#e7f3ff,stroke:#0066cc,stroke-width:2px,color:#003d7a

%% Application des styles
class FinalSuccess,StepSuccess,LogAPISuccess,AllStepsComplete successClass
class ErrorEnv,ErrorConfig,ErrorAPI,ErrorHoliday,ErrorTimeSlot,ErrorUsers,ErrorBrowser,StepFailure,StopOnError errorClass
class StepWarning,SaveUnknownStatus,LogAPIError,LogNoInscription warningClass
class Start,LoadEnv,LoadConfig,CreateDirs1,CreateDirs2,LoadUsers,LaunchBrowser,CreateContext,CreatePage,StartTracing,InitExecution,ExecuteSteps processClass
class ValidateEnv,ValidateConfig,CheckLectureMode,APISuccess,IsHoliday,CheckHolidayFlag,InTimeSlot,ValidateUsers,BrowserSuccess,NextStep,StepResult,ErrorType,AppErrorFound,CheckInscription,APIInscriptionSuccess decisionClass
class CallAPI,MergeConfig,HandleAPIError,SendToAPI apiClass
```
