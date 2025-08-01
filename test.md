```mermaid

flowchart TD
Start([🚀 DÉBUT EXÉCUTION<br/>SCÉNARIO]) --> InitEnv[📋 Chargement variables<br/>environnement SCENARIO]


%% Vérification variable SCENARIO obligatoire
InitEnv --> CheckScenario{Variable SCENARIO<br/>définie ?}
CheckScenario -->|NON| ErrorScenario[❌ ERREUR FATALE<br/>Variable SCENARIO manquante<br/>EXIT CODE 2]

%% Chargement configuration fichiers
CheckScenario -->|OUI| LoadConfig[📁 Chargement configuration<br/>fichier YAML scénario]
LoadConfig --> ConfigExists{Fichier configuration<br/>existe ?}
ConfigExists -->|NON| ErrorConfig[❌ ERREUR FATALE<br/>Fichier configuration<br/>introuvable<br/>EXIT CODE 2]

%% Chargement configuration commune
ConfigExists -->|OUI| CheckCommonConfig{Configuration<br/>commune définie ?}
CheckCommonConfig -->|OUI| LoadCommonConfig[📁 Chargement<br/>configuration commune]
LoadCommonConfig --> CommonExists{Fichier commun<br/>existe ?}
CommonExists -->|NON| ErrorCommonConfig[❌ ERREUR FATALE<br/>Configuration commune<br/>introuvable<br/>EXIT CODE 2]
CommonExists -->|OUI| MergeConfigs[🔄 Fusion configurations<br/>commune + scénario]
CheckCommonConfig -->|NON| ValidateURL[🔍 Validation URL initiale]
MergeConfigs --> ValidateURL

%% Validation URL initiale
ValidateURL --> URLExists{URL initiale définie<br/>pour la plateforme ?}
URLExists -->|NON| ErrorURL[❌ ERREUR FATALE<br/>URL initiale manquante<br/>pour la plateforme<br/>EXIT CODE 2]

%% Vérification mode lecture API
URLExists -->|OUI| CheckAPIMode{LECTURE=true ?}

%% Mode API désactivé (legacy)
CheckAPIMode -->|NON| LegacyMode[📝 Mode Legacy<br/>Pas d'appel API<br/>Configuration locale]
LegacyMode --> CreateDirs[📂 Création répertoires<br/>screenshots/rapports]

%% Mode API activé
CheckAPIMode -->|OUI| CallAPI[🌐 Appel API injecteur<br/>Récupération données scénario]
CallAPI --> APISuccess{Appel API<br/>réussi ?}

%% Erreur API - Gestion selon INSCRIPTION
APISuccess -->|NON| CheckInscription{INSCRIPTION=true ?}
CheckInscription -->|OUI| ErrorAPIFatal[❌ ERREUR FATALE<br/>API inaccessible<br/>Inscription impossible<br/>EXIT CODE 2]
CheckInscription -->|NON| WarnAPIOffline[⚠️ AVERTISSEMENT<br/>API inaccessible<br/>Mode dégradé<br/>Configuration locale]
WarnAPIOffline --> CreateDirs

%% Succès API - Vérification planning
APISuccess -->|OUI| CheckPlanning[📅 Vérification planning<br/>d'exécution]
CheckPlanning --> IsHoliday{Jour férié<br/>aujourd'hui ?}

%% Gestion jours fériés
IsHoliday -->|OUI| CheckHolidayFlag{flag_ferie = true<br/>dans API ?}
CheckHolidayFlag -->|NON| ErrorHoliday[❌ ARRÊT PLANIFIÉ<br/>Scénario interdit<br/>les jours fériés<br/>EXIT CODE 2]
CheckHolidayFlag -->|OUI| CheckTimeSlots1[⏰ Vérification<br/>plages horaires]

%% Jour normal
IsHoliday -->|NON| CheckTimeSlots2[⏰ Vérification<br/>plages horaires]

%% Vérification plages horaires
CheckTimeSlots1 --> HasTimeSlots{Plages horaires<br/>définies aujourd'hui ?}
CheckTimeSlots2 --> HasTimeSlots
HasTimeSlots -->|NON| ErrorNoSlots[❌ ARRÊT PLANIFIÉ<br/>Aucune plage horaire<br/>pour aujourd'hui<br/>EXIT CODE 2]

HasTimeSlots -->|OUI| TimeInRange{Heure actuelle<br/>dans plage autorisée ?}
TimeInRange -->|NON| ErrorTimeOut[❌ ARRÊT PLANIFIÉ<br/>Heure hors plages<br/>autorisées<br/>EXIT CODE 2]

%% Planning OK - Suite du processus
TimeInRange -->|OUI| CreateDirs

%% Création répertoires et gestion utilisateurs
CreateDirs --> DirSuccess{Répertoires créés<br/>avec succès ?}
DirSuccess -->|NON| WarnDirs[⚠️ AVERTISSEMENT<br/>Échec création répertoires<br/>Pas de screenshots/rapports]
DirSuccess -->|OUI| CheckISACUser{Utilisateur ISAC<br/>défini ?}
WarnDirs --> CheckISACUser

%% Gestion utilisateur ISAC
CheckISACUser -->|OUI| LoadISACUser[🔐 Chargement et<br/>déchiffrement utilisateur ISAC]
LoadISACUser --> ISACSuccess{Utilisateur ISAC<br/>chargé ?}
ISACSuccess -->|NON| ErrorISAC[❌ ERREUR FATALE<br/>Échec chargement<br/>utilisateur ISAC<br/>EXIT CODE 2]
ISACSuccess -->|OUI| LaunchBrowser[🌐 Lancement navigateur<br/>Playwright]
CheckISACUser -->|NON| LaunchBrowser

%% Lancement navigateur
LaunchBrowser --> BrowserSuccess{Navigateur lancé<br/>avec succès ?}
BrowserSuccess -->|NON| ErrorBrowser[❌ ERREUR FATALE<br/>Échec lancement navigateur<br/>Playwright non installé ?<br/>EXIT CODE 2]

%% Création contexte et première page
BrowserSuccess -->|OUI| CreateContext[🎭 Création contexte<br/>navigateur + première page]
CreateContext --> ContextSuccess{Contexte créé<br/>avec succès ?}
ContextSuccess -->|NON| ErrorContext[❌ ERREUR FATALE<br/>Échec création contexte<br/>EXIT CODE 2]

%% Début exécution des étapes
ContextSuccess -->|OUI| StartExecution[▶️ DÉBUT EXÉCUTION<br/>DES ÉTAPES]
StartExecution --> ExecuteStep[🎯 Exécution étape N<br/>Compteur += 1]

%% Boucle d'exécution des étapes
ExecuteStep --> StepSuccess{Étape réussie ?}

%% Cas d'erreur dans une étape
StepSuccess -->|NON| HandleStepError[🚨 Gestion exception<br/>étape]
HandleStepError --> CheckTimeout{Exception<br/>de timeout ?}

%% Gestion timeout avec vérification erreurs applicatives
CheckTimeout -->|OUI| CheckErrorPatterns[🔍 Vérification patterns<br/>d'erreurs dans la page]
CheckErrorPatterns --> ErrorPatternsFound{Erreurs applicatives<br/>détectées ?}
ErrorPatternsFound -->|OUI| AppError[❌ ERREUR APPLICATIVE<br/>Timeout dû à erreur serveur<br/>(4xx/5xx détectée)]
ErrorPatternsFound -->|NON| TimeoutError[❌ ERREUR TIMEOUT<br/>Élément non trouvé<br/>dans les délais]

%% Autres types d'erreurs
CheckTimeout -->|NON| OtherError[❌ AUTRE ERREUR<br/>Navigation, sélecteur, etc.]

%% Toutes les erreurs d'étapes mènent à l'arrêt
AppError --> TakeErrorScreenshot[📸 Capture d'écran<br/>d'erreur]
TimeoutError --> TakeErrorScreenshot
OtherError --> TakeErrorScreenshot
TakeErrorScreenshot --> FinalizeError[📊 Finalisation étape<br/>Status: ÉCHEC (2)]
FinalizeError --> SaveErrorReport[💾 Sauvegarde rapport<br/>JSON avec erreur]
SaveErrorReport --> ExitError[❌ ARRÊT EXÉCUTION<br/>EXIT CODE 2]

%% Cas de succès d'étape
StepSuccess -->|OUI| TakeScreenshot[📸 Capture d'écran<br/>de succès (si configurée)]
TakeScreenshot --> FinalizeStep[📊 Finalisation étape<br/>Status: SUCCÈS (0)]
FinalizeStep --> MoreSteps{Autres étapes<br/>à exécuter ?}
MoreSteps -->|OUI| ExecuteStep

%% Fin de toutes les étapes - Succès
MoreSteps -->|NON| AllStepsComplete[✅ TOUTES LES ÉTAPES<br/>TERMINÉES AVEC SUCCÈS]
AllStepsComplete --> FinalizeExecution[📊 Finalisation exécution<br/>Calcul durée totale]
FinalizeExecution --> SaveSuccessReport[💾 Sauvegarde rapport<br/>JSON de succès]
SaveSuccessReport --> CheckAPIInscription{INSCRIPTION=true<br/>et API disponible ?}

%% Inscription API des résultats
CheckAPIInscription -->|OUI| SendToAPI[📤 Envoi résultats<br/>vers API injecteur]
SendToAPI --> APIInscriptionSuccess{Inscription API<br/>réussie ?}
APIInscriptionSuccess -->|NON| WarnAPIInscription[⚠️ AVERTISSEMENT<br/>Échec inscription API<br/>Résultats sauvés localement]
APIInscriptionSuccess -->|OUI| SuccessWithAPI[🎉 SUCCÈS COMPLET<br/>Résultats en base]

CheckAPIInscription -->|NON| SuccessLocal[🎉 SUCCÈS LOCAL<br/>Pas d'inscription API]
WarnAPIInscription --> SuccessLocal

%% Nettoyage final
SuccessWithAPI --> Cleanup[🧹 Nettoyage<br/>Fermeture navigateur<br/>Sauvegarde traces]
SuccessLocal --> Cleanup
Cleanup --> ExitSuccess[✅ FIN NORMALE<br/>EXIT CODE 0]

%% Classes de style
classDef successClass fill:#d4edda,stroke:#28a745,stroke-width:2px,color:#155724
classDef errorClass fill:#f8d7da,stroke:#dc3545,stroke-width:2px,color:#721c24
classDef warningClass fill:#fff3cd,stroke:#ffc107,stroke-width:2px,color:#856404
classDef processClass fill:#e2e3e5,stroke:#6c757d,stroke-width:2px,color:#495057
classDef decisionClass fill:#cce5ff,stroke:#007bff,stroke-width:2px,color:#004085
classDef apiClass fill:#e7f3ff,stroke:#0066cc,stroke-width:2px,color:#003d7a

%% Application des styles
class ExitSuccess,SuccessWithAPI,SuccessLocal,AllStepsComplete,FinalizeStep,TakeScreenshot successClass
class ErrorScenario,ErrorConfig,ErrorCommonConfig,ErrorURL,ErrorAPIFatal,ErrorHoliday,ErrorNoSlots,ErrorTimeOut,ErrorISAC,ErrorBrowser,ErrorContext,ExitError,AppError,TimeoutError,OtherError errorClass
class WarnAPIOffline,WarnDirs,WarnAPIInscription warningClass
class Start,InitEnv,LoadConfig,LoadCommonConfig,MergeConfigs,ValidateURL,LegacyMode,CreateDirs,LoadISACUser,LaunchBrowser,CreateContext,StartExecution,ExecuteStep,HandleStepError,TakeErrorScreenshot,FinalizeError,SaveErrorReport,FinalizeExecution,SaveSuccessReport,Cleanup processClass
class CheckScenario,ConfigExists,CheckCommonConfig,CommonExists,URLExists,CheckAPIMode,APISuccess,CheckInscription,IsHoliday,CheckHolidayFlag,HasTimeSlots,TimeInRange,DirSuccess,CheckISACUser,ISACSuccess,BrowserSuccess,ContextSuccess,StepSuccess,CheckTimeout,ErrorPatternsFound,MoreSteps,CheckAPIInscription,APIInscriptionSuccess decisionClass
class CallAPI,CheckPlanning,CheckTimeSlots1,CheckTimeSlots2,SendToAPI apiClass
```
