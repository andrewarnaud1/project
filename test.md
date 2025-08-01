```mermaid

flowchart TD
Start([ DÉBUT EXÉCUTION SCÉNARIO]) --> InitEnv[ Chargement variables environnement SCENARIO]


%% Vérification variable SCENARIO obligatoire
InitEnv --> CheckScenario{Variable SCENARIO définie ?}
CheckScenario -->|NON| ErrorScenario[ ERREUR FATALE Variable SCENARIO manquante EXIT CODE 2]

%% Chargement configuration fichiers
CheckScenario -->|OUI| LoadConfig[ Chargement configuration fichier YAML scénario]
LoadConfig --> ConfigExists{Fichier configuration existe ?}
ConfigExists -->|NON| ErrorConfig[ ERREUR FATALE Fichier configuration introuvable EXIT CODE 2]

%% Chargement configuration commune
ConfigExists -->|OUI| CheckCommonConfig{Configuration commune définie ?}
CheckCommonConfig -->|OUI| LoadCommonConfig[ Chargement configuration commune]
LoadCommonConfig --> CommonExists{Fichier commun existe ?}
CommonExists -->|NON| ErrorCommonConfig[ ERREUR FATALE Configuration commune introuvable EXIT CODE 2]
CommonExists -->|OUI| MergeConfigs[ Fusion configurations commune + scénario]
CheckCommonConfig -->|NON| ValidateURL[ Validation URL initiale]
MergeConfigs --> ValidateURL

%% Validation URL initiale
ValidateURL --> URLExists{URL initiale définie pour la plateforme ?}
URLExists -->|NON| ErrorURL[ ERREUR FATALE URL initiale manquante pour la plateforme EXIT CODE 2]

%% Vérification mode lecture API
URLExists -->|OUI| CheckAPIMode{LECTURE=true ?}

%% Mode API désactivé (legacy)
CheckAPIMode -->|NON| LegacyMode[ Mode Legacy Pas d'appel API Configuration locale]
LegacyMode --> CreateDirs[ Création répertoires screenshots/rapports]

%% Mode API activé
CheckAPIMode -->|OUI| CallAPI[ Appel API injecteur Récupération données scénario]
CallAPI --> APISuccess{Appel API réussi ?}

%% Erreur API - Gestion selon INSCRIPTION
APISuccess -->|NON| CheckInscription{INSCRIPTION=true ?}
CheckInscription -->|OUI| ErrorAPIFatal[ ERREUR FATALE API inaccessible Inscription impossible EXIT CODE 2]
CheckInscription -->|NON| WarnAPIOffline[⚠ AVERTISSEMENT API inaccessible Mode dégradé Configuration locale]
WarnAPIOffline --> CreateDirs

%% Succès API - Vérification planning
APISuccess -->|OUI| CheckPlanning[ Vérification planning d'exécution]
CheckPlanning --> IsHoliday{Jour férié aujourd'hui ?}

%% Gestion jours fériés
IsHoliday -->|OUI| CheckHolidayFlag{flag_ferie = true dans API ?}
CheckHolidayFlag -->|NON| ErrorHoliday[ ARRÊT PLANIFIÉ Scénario interdit les jours fériés EXIT CODE 2]
CheckHolidayFlag -->|OUI| CheckTimeSlots1[ Vérification plages horaires]

%% Jour normal
IsHoliday -->|NON| CheckTimeSlots2[ Vérification plages horaires]

%% Vérification plages horaires
CheckTimeSlots1 --> HasTimeSlots{Plages horaires définies aujourd'hui ?}
CheckTimeSlots2 --> HasTimeSlots
HasTimeSlots -->|NON| ErrorNoSlots[ ARRÊT PLANIFIÉ Aucune plage horaire pour aujourd'hui EXIT CODE 2]

HasTimeSlots -->|OUI| TimeInRange{Heure actuelle dans plage autorisée ?}
TimeInRange -->|NON| ErrorTimeOut[ ARRÊT PLANIFIÉ Heure hors plages autorisées EXIT CODE 2]

%% Planning OK - Suite du processus
TimeInRange -->|OUI| CreateDirs

%% Création répertoires et gestion utilisateurs
CreateDirs --> DirSuccess{Répertoires créés avec succès ?}
DirSuccess -->|NON| WarnDirs[ AVERTISSEMENT Échec création répertoires Pas de screenshots/rapports]
DirSuccess -->|OUI| CheckISACUser{Utilisateur ISAC défini ?}
WarnDirs --> CheckISACUser

%% Gestion utilisateur ISAC
CheckISACUser -->|OUI| LoadISACUser[ Chargement et déchiffrement utilisateur ISAC]
LoadISACUser --> ISACSuccess{Utilisateur ISAC chargé ?}
ISACSuccess -->|NON| ErrorISAC[ ERREUR FATALE Échec chargement utilisateur ISAC EXIT CODE 2]
ISACSuccess -->|OUI| LaunchBrowser[ Lancement navigateur Playwright]
CheckISACUser -->|NON| LaunchBrowser

%% Lancement navigateur
LaunchBrowser --> BrowserSuccess{Navigateur lancé avec succès ?}
BrowserSuccess -->|NON| ErrorBrowser[ ERREUR FATALE Échec lancement navigateur Playwright non installé ? EXIT CODE 2]

%% Création contexte et première page
BrowserSuccess -->|OUI| CreateContext[ Création contexte navigateur + première page]
CreateContext --> ContextSuccess{Contexte créé avec succès ?}
ContextSuccess -->|NON| ErrorContext[ ERREUR FATALE Échec création contexte EXIT CODE 2]

%% Début exécution des étapes
ContextSuccess -->|OUI| StartExecution[ DÉBUT EXÉCUTION DES ÉTAPES]
StartExecution --> ExecuteStep[ Exécution étape N Compteur += 1]

%% Boucle d'exécution des étapes
ExecuteStep --> StepSuccess{Étape réussie ?}

%% Cas d'erreur dans une étape
StepSuccess -->|NON| HandleStepError[ Gestion exception étape]
HandleStepError --> CheckTimeout{Exception de timeout ?}

%% Gestion timeout avec vérification erreurs applicatives
CheckTimeout -->|OUI| CheckErrorPatterns[ Vérification patterns d'erreurs dans la page]
CheckErrorPatterns --> ErrorPatternsFound{Erreurs applicatives détectées ?}
ErrorPatternsFound -->|OUI| AppError[ ERREUR APPLICATIVE Timeout dû à erreur serveur (4xx/5xx détectée)]
ErrorPatternsFound -->|NON| TimeoutError[ ERREUR TIMEOUT Élément non trouvé dans les délais]

%% Autres types d'erreurs
CheckTimeout -->|NON| OtherError[ AUTRE ERREUR Navigation, sélecteur, etc.]

%% Toutes les erreurs d'étapes mènent à l'arrêt
AppError --> TakeErrorScreenshot[ Capture d'écran d'erreur]
TimeoutError --> TakeErrorScreenshot
OtherError --> TakeErrorScreenshot
TakeErrorScreenshot --> FinalizeError[ Finalisation étape Status: ÉCHEC (2)]
FinalizeError --> SaveErrorReport[ Sauvegarde rapport JSON avec erreur]
SaveErrorReport --> ExitError[ ARRÊT EXÉCUTION EXIT CODE 2]

%% Cas de succès d'étape
StepSuccess -->|OUI| TakeScreenshot[ Capture d'écran de succès (si configurée)]
TakeScreenshot --> FinalizeStep[ Finalisation étape Status: SUCCÈS (0)]
FinalizeStep --> MoreSteps{Autres étapes à exécuter ?}
MoreSteps -->|OUI| ExecuteStep

%% Fin de toutes les étapes - Succès
MoreSteps -->|NON| AllStepsComplete[ TOUTES LES ÉTAPES TERMINÉES AVEC SUCCÈS]
AllStepsComplete --> FinalizeExecution[ Finalisation exécution Calcul durée totale]
FinalizeExecution --> SaveSuccessReport[ Sauvegarde rapport JSON de succès]
SaveSuccessReport --> CheckAPIInscription{INSCRIPTION=true et API disponible ?}

%% Inscription API des résultats
CheckAPIInscription -->|OUI| SendToAPI[ Envoi résultats vers API injecteur]
SendToAPI --> APIInscriptionSuccess{Inscription API réussie ?}
APIInscriptionSuccess -->|NON| WarnAPIInscription[⚠ AVERTISSEMENT Échec inscription API Résultats sauvés localement]
APIInscriptionSuccess -->|OUI| SuccessWithAPI[ SUCCÈS COMPLET Résultats en base]

CheckAPIInscription -->|NON| SuccessLocal[ SUCCÈS LOCAL Pas d'inscription API]
WarnAPIInscription --> SuccessLocal

%% Nettoyage final
SuccessWithAPI --> Cleanup[ Nettoyage Fermeture navigateur Sauvegarde traces]
SuccessLocal --> Cleanup
Cleanup --> ExitSuccess[ FIN NORMALE EXIT CODE 0]

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
