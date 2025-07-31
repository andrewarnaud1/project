```mermaid
flowchart TD
    Start([🚀 DÉBUT EXÉCUTION<br/>pytest execution]) --> CheckScenarioVar{Variable SCENARIO<br/>définie ?}
    
    %% Erreur variable manquante
    CheckScenarioVar -->|❌ NON| ErrorScenario[❌ ERREUR CRITIQUE<br/>Variable SCENARIO manquante]
    ErrorScenario --> ExitCritical1[🛑 pytest.exit(2)<br/>ARRÊT IMMÉDIAT]
    
    %% Initialisation normale
    CheckScenarioVar -->|✅ OUI| InitExecution[📋 Initialisation Execution<br/>__init__()]
    
    InitExecution --> LoadEnvVars[🌍 Chargement variables<br/>environnement]
    
    LoadEnvVars --> LoadConfigFile{Fichier config<br/>scenario trouvé ?}
    
    %% Erreur fichier config
    LoadConfigFile -->|❌ NON| ErrorConfigFile[❌ ERREUR CRITIQUE<br/>Fichier config introuvable]
    ErrorConfigFile --> ExitCritical2[🛑 pytest.exit(2)<br/>ARRÊT IMMÉDIAT]
    
    %% Configuration OK
    LoadConfigFile -->|✅ OUI| LoadCommonConfig{Config commune<br/>requise ?}
    
    LoadCommonConfig -->|✅ OUI| CheckCommonFile{Fichier commun<br/>trouvé ?}
    LoadCommonConfig -->|❌ NON| ConfigLoaded[⚙️ Configuration chargée]
    
    %% Erreur config commune
    CheckCommonFile -->|❌ NON| ErrorCommonFile[❌ ERREUR CRITIQUE<br/>Config commune introuvable]
    ErrorCommonFile --> ExitCritical3[🛑 pytest.exit(2)<br/>ARRÊT IMMÉDIAT]
    
    CheckCommonFile -->|✅ OUI| ConfigLoaded
    
    ConfigLoaded --> CheckLectureMode{Mode LECTURE<br/>activé ?}
    
    %% ========== BRANCHE LECTURE = FALSE ==========
    CheckLectureMode -->|❌ NON - LECTURE=false| NoAPIMode[📝 MODE LEGACY<br/>Pas d'appel API<br/>donnees_scenario_api = {}]
    
    NoAPIMode --> FinalizeConfigNoAPI[🔧 Finalisation configuration<br/>sans données API]
    
    FinalizeConfigNoAPI --> CreateDirectories1[📁 Création répertoires<br/>screenshots/rapports]
    
    CreateDirectories1 --> DirectorySuccess1{Répertoires<br/>créés ?}
    
    DirectorySuccess1 -->|❌ NON| WarnDirectories1[⚠️ WARNING<br/>Pas de screenshots/rapports]
    DirectorySuccess1 -->|✅ OUI| ReadyLegacy[✅ PRÊT EXÉCUTION LEGACY]
    WarnDirectories1 --> ReadyLegacy
    
    ReadyLegacy --> LaunchBrowserLegacy[🌐 Lancement navigateur<br/>Playwright]
    
    %% ========== BRANCHE LECTURE = TRUE ==========
    CheckLectureMode -->|✅ OUI - LECTURE=true| CallAPI[🌐 APPEL API<br/>lecture_api_scenario()]
    
    CallAPI --> APIResult{Résultat API}
    
    %% ========== CAS ERREUR API ==========
    APIResult -->|❌ ERREUR HTTP| HandleHTTPError[🚨 Erreur HTTP détectée<br/>Status Code: 4xx/5xx]
    APIResult -->|❌ TIMEOUT| HandleTimeoutError[⏰ Timeout API<br/>Pas de réponse]
    APIResult -->|❌ CONNEXION| HandleConnectionError[🔌 Erreur connexion<br/>Serveur inaccessible]
    APIResult -->|❌ JSON INVALIDE| HandleJSONError[📄 Réponse API invalide<br/>JSON malformé]
    APIResult -->|❌ AUTRE ERREUR| HandleOtherError[❓ Erreur inconnue API]
    
    HandleHTTPError --> SetInfrastructureError1[📊 Status = 3 UNKNOWN<br/>Type: Infrastructure<br/>Commentaire: Erreur HTTP API]
    HandleTimeoutError --> SetInfrastructureError2[📊 Status = 3 UNKNOWN<br/>Type: Infrastructure<br/>Commentaire: Timeout API]
    HandleConnectionError --> SetInfrastructureError3[📊 Status = 3 UNKNOWN<br/>Type: Infrastructure<br/>Commentaire: Connexion API]
    HandleJSONError --> SetInfrastructureError4[📊 Status = 3 UNKNOWN<br/>Type: Infrastructure<br/>Commentaire: Réponse API]
    HandleOtherError --> SetInfrastructureError5[📊 Status = 3 UNKNOWN<br/>Type: Infrastructure<br/>Commentaire: Erreur API]
    
    SetInfrastructureError1 --> CreateErrorReport1[📄 Génération rapport JSON<br/>erreur infrastructure]
    SetInfrastructureError2 --> CreateErrorReport2[📄 Génération rapport JSON<br/>erreur infrastructure]
    SetInfrastructureError3 --> CreateErrorReport3[📄 Génération rapport JSON<br/>erreur infrastructure]
    SetInfrastructureError4 --> CreateErrorReport4[📄 Génération rapport JSON<br/>erreur infrastructure]
    SetInfrastructureError5 --> CreateErrorReport5[📄 Génération rapport JSON<br/>erreur infrastructure]
    
    CreateErrorReport1 --> ExitInfrastructure1[🛑 pytest.exit(3)<br/>ARRÊT INFRASTRUCTURE]
    CreateErrorReport2 --> ExitInfrastructure2[🛑 pytest.exit(3)<br/>ARRÊT INFRASTRUCTURE]
    CreateErrorReport3 --> ExitInfrastructure3[🛑 pytest.exit(3)<br/>ARRÊT INFRASTRUCTURE]
    CreateErrorReport4 --> ExitInfrastructure4[🛑 pytest.exit(3)<br/>ARRÊT INFRASTRUCTURE]
    CreateErrorReport5 --> ExitInfrastructure5[🛑 pytest.exit(3)<br/>ARRÊT INFRASTRUCTURE]
    
    %% ========== CAS SUCCÈS API ==========
    APIResult -->|✅ SUCCÈS 200| StoreAPIData[📦 Stockage données API<br/>donnees_scenario_api]
    
    StoreAPIData --> FinalizeConfigAPI[🔧 Finalisation configuration<br/>avec données API]
    
    FinalizeConfigAPI --> CreateDirectories2[📁 Création répertoires<br/>avec noms API]
    
    CreateDirectories2 --> DirectorySuccess2{Répertoires<br/>créés ?}
    
    DirectorySuccess2 -->|❌ NON| WarnDirectories2[⚠️ WARNING<br/>Pas de screenshots/rapports]
    DirectorySuccess2 -->|✅ OUI| CheckPlanningData{Données planning<br/>présentes ?}
    WarnDirectories2 --> CheckPlanningData
    
    %% ========== VÉRIFICATION PLANNING ==========
    CheckPlanningData -->|❌ NON| NoPlanningData[⚠️ Pas de données planning<br/>Exécution autorisée par défaut]
    CheckPlanningData -->|✅ OUI| VerifyPlanning[📅 Vérification planning<br/>verifier_planning_execution()]
    
    NoPlanningData --> ReadyWithAPI[✅ PRÊT EXÉCUTION API<br/>Sans vérification planning]
    
    VerifyPlanning --> PlanningResult{Résultat planning}
    
    %% ========== CAS PLANNING VIOLÉ ==========
    PlanningResult -->|❌ JOUR FÉRIÉ| PlanningHoliday[🎄 Jour férié interdit<br/>flag_ferie ≠ true]
    PlanningResult -->|❌ HORS PLAGE| PlanningOutOfRange[⏰ Heure hors plage<br/>Créneaux non respectés]
    PlanningResult -->|❌ JOUR NON PROGRAMMÉ| PlanningNoDay[📅 Jour non programmé<br/>Aucune plage définie]
    PlanningResult -->|❌ ERREUR PLANNING| PlanningError[❓ Erreur vérification<br/>Données planning invalides]
    
    PlanningHoliday --> SetPlanningError1[📊 Status = 2 FAILED<br/>Type: Planning<br/>Commentaire: Jour férié]
    PlanningOutOfRange --> SetPlanningError2[📊 Status = 2 FAILED<br/>Type: Planning<br/>Commentaire: Hors plage]
    PlanningNoDay --> SetPlanningError3[📊 Status = 2 FAILED<br/>Type: Planning<br/>Commentaire: Jour non programmé]
    PlanningError --> SetPlanningError4[📊 Status = 2 FAILED<br/>Type: Planning<br/>Commentaire: Erreur planning]
    
    SetPlanningError1 --> CreatePlanningReport1[📄 Génération rapport JSON<br/>violation planning]
    SetPlanningError2 --> CreatePlanningReport2[📄 Génération rapport JSON<br/>violation planning]
    SetPlanningError3 --> CreatePlanningReport3[📄 Génération rapport JSON<br/>violation planning]
    SetPlanningError4 --> CreatePlanningReport4[📄 Génération rapport JSON<br/>violation planning]
    
    CreatePlanningReport1 --> ExitPlanning1[🛑 pytest.exit(2)<br/>ARRÊT PLANNING]
    CreatePlanningReport2 --> ExitPlanning2[🛑 pytest.exit(2)<br/>ARRÊT PLANNING]
    CreatePlanningReport3 --> ExitPlanning3[🛑 pytest.exit(2)<br/>ARRÊT PLANNING]
    CreatePlanningReport4 --> ExitPlanning4[🛑 pytest.exit(2)<br/>ARRÊT PLANNING]
    
    %% ========== CAS PLANNING OK ==========
    PlanningResult -->|✅ AUTORISÉ| PlanningAuthorized[✅ Planning respecté<br/>Exécution autorisée]
    
    PlanningAuthorized --> ReadyWithAPI
    ReadyWithAPI --> LaunchBrowserAPI[🌐 Lancement navigateur<br/>Playwright avec données API]
    
    %% ========== EXÉCUTION DES TESTS ==========
    LaunchBrowserLegacy --> BrowserResult1{Lancement<br/>navigateur ?}
    LaunchBrowserAPI --> BrowserResult2{Lancement<br/>navigateur ?}
    
    %% Erreur lancement navigateur
    BrowserResult1 -->|❌ ERREUR| BrowserError1[🌐 Erreur Playwright<br/>Navigateur non disponible]
    BrowserResult2 -->|❌ ERREUR| BrowserError2[🌐 Erreur Playwright<br/>Navigateur non disponible]
    
    BrowserError1 --> SetBrowserError1[📊 Status = 3 UNKNOWN<br/>Type: Infrastructure<br/>Commentaire: Erreur navigateur]
    BrowserError2 --> SetBrowserError2[📊 Status = 3 UNKNOWN<br/>Type: Infrastructure<br/>Commentaire: Erreur navigateur]
    
    SetBrowserError1 --> CreateBrowserReport1[📄 Génération rapport JSON<br/>erreur navigateur]
    SetBrowserError2 --> CreateBrowserReport2[📄 Génération rapport JSON<br/>erreur navigateur]
    
    CreateBrowserReport1 --> ExitBrowser1[🛑 pytest.exit(2)<br/>ARRÊT NAVIGATEUR]
    CreateBrowserReport2 --> ExitBrowser2[🛑 pytest.exit(2)<br/>ARRÊT NAVIGATEUR]
    
    %% Navigateur OK
    BrowserResult1 -->|✅ OK| RunTests1[🎬 Exécution des tests<br/>Mode Legacy]
    BrowserResult2 -->|✅ OK| RunTests2[🎬 Exécution des tests<br/>Mode API]
    
    RunTests1 --> TestExecution1{Résultat<br/>tests ?}
    RunTests2 --> TestExecution2{Résultat<br/>tests ?}
    
    %% ========== RÉSULTATS TESTS ==========
    
    %% Tests réussis
    TestExecution1 -->|✅ SUCCÈS| TestSuccess1[🎯 Tous tests réussis<br/>Toutes étapes OK]
    TestExecution2 -->|✅ SUCCÈS| TestSuccess2[🎯 Tous tests réussis<br/>Toutes étapes OK]
    
    TestSuccess1 --> SetSuccess1[📊 Status = 0 SUCCESS<br/>Type: Fonctionnel<br/>Commentaire: Succès]
    TestSuccess2 --> SetSuccess2[📊 Status = 0 SUCCESS<br/>Type: Fonctionnel<br/>Commentaire: Succès]
    
    %% Tests échoués
    TestExecution1 -->|❌ ÉCHEC| TestFailed1[💥 Tests échoués<br/>Erreur fonctionnelle]
    TestExecution2 -->|❌ ÉCHEC| TestFailed2[💥 Tests échoués<br/>Erreur fonctionnelle]
    
    TestFailed1 --> SetFailed1[📊 Status = 2 FAILED<br/>Type: Fonctionnel<br/>Commentaire: Échec test]
    TestFailed2 --> SetFailed2[📊 Status = 2 FAILED<br/>Type: Fonctionnel<br/>Commentaire: Échec test]
    
    %% Erreur technique tests
    TestExecution1 -->|🚨 ERREUR| TestError1[🚨 Erreur technique<br/>Problème infrastructure]
    TestExecution2 -->|🚨 ERREUR| TestError2[🚨 Erreur technique<br/>Problème infrastructure]
    
    TestError1 --> SetTestError1[📊 Status = 3 UNKNOWN<br/>Type: Infrastructure<br/>Commentaire: Erreur technique]
    TestError2 --> SetTestError2[📊 Status = 3 UNKNOWN<br/>Type: Infrastructure<br/>Commentaire: Erreur technique]
    
    %% ========== FINALISATION ==========
    SetSuccess1 --> Finalize1[📊 Calcul durée<br/>Agrégation résultats]
    SetSuccess2 --> Finalize2[📊 Calcul durée<br/>Agrégation résultats]
    SetFailed1 --> Finalize3[📊 Calcul durée<br/>Agrégation résultats]
    SetFailed2 --> Finalize4[📊 Calcul durée<br/>Agrégation résultats]
    SetTestError1 --> Finalize5[📊 Calcul durée<br/>Agrégation résultats]
    SetTestError2 --> Finalize6[📊 Calcul durée<br/>Agrégation résultats]
    
    Finalize1 --> SaveJSON1[💾 Sauvegarde rapport JSON<br/>Status: SUCCESS]
    Finalize2 --> SaveJSON2[💾 Sauvegarde rapport JSON<br/>Status: SUCCESS]
    Finalize3 --> SaveJSON3[💾 Sauvegarde rapport JSON<br/>Status: FAILED]
    Finalize4 --> SaveJSON4[💾 Sauvegarde rapport JSON<br/>Status: FAILED]
    Finalize5 --> SaveJSON5[💾 Sauvegarde rapport JSON<br/>Status: UNKNOWN]
    Finalize6 --> SaveJSON6[💾 Sauvegarde rapport JSON<br/>Status: UNKNOWN]
    
    %% ========== INSCRIPTION API ==========
    SaveJSON1 --> CheckInscription1{INSCRIPTION<br/>activée ?}
    SaveJSON2 --> CheckInscription2{INSCRIPTION<br/>activée ?}
    SaveJSON3 --> CheckInscription3{INSCRIPTION<br/>activée ?}
    SaveJSON4 --> CheckInscription4{INSCRIPTION<br/>activée ?}
    SaveJSON5 --> CheckInscription5{INSCRIPTION<br/>activée ?}
    SaveJSON6 --> CheckInscription6{INSCRIPTION<br/>activée ?}
    
    %% Inscription OUI
    CheckInscription1 -->|✅ OUI| SendAPI1[📤 Inscription résultats<br/>inscrire_resultats_api]
    CheckInscription2 -->|✅ OUI| SendAPI2[📤 Inscription résultats<br/>inscrire_resultats_api]
    CheckInscription3 -->|✅ OUI| SendAPI3[📤 Inscription résultats<br/>inscrire_resultats_api]
    CheckInscription4 -->|✅ OUI| SendAPI4[📤 Inscription résultats<br/>inscrire_resultats_api]
    CheckInscription5 -->|✅ OUI| SendAPI5[📤 Inscription résultats<br/>inscrire_resultats_api]
    CheckInscription6 -->|✅ OUI| SendAPI6[📤 Inscription résultats<br/>inscrire_resultats_api]
    
    %% Inscription NON
    CheckInscription1 -->|❌ NON| LocalOnly1[📝 Log local uniquement<br/>Pas d'inscription]
    CheckInscription2 -->|❌ NON| LocalOnly2[📝 Log local uniquement<br/>Pas d'inscription]
    CheckInscription3 -->|❌ NON| LocalOnly3[📝 Log local uniquement<br/>Pas d'inscription]
    CheckInscription4 -->|❌ NON| LocalOnly4[📝 Log local uniquement<br/>Pas d'inscription]
    CheckInscription5 -->|❌ NON| LocalOnly5[📝 Log local uniquement<br/>Pas d'inscription]
    CheckInscription6 -->|❌ NON| LocalOnly6[📝 Log local uniquement<br/>Pas d'inscription]
    
    %% ========== FINS D'EXÉCUTION ==========
    SendAPI1 --> EndSuccess1[🏁 FIN SUCCÈS<br/>Exit Code: 0]
    SendAPI2 --> EndSuccess2[🏁 FIN SUCCÈS<br/>Exit Code: 0]
    LocalOnly1 --> EndSuccess1
    LocalOnly2 --> EndSuccess2
    
    SendAPI3 --> EndFailed1[🏁 FIN ÉCHEC<br/>Exit Code: 2]
    SendAPI4 --> EndFailed2[🏁 FIN ÉCHEC<br/>Exit Code: 2]
    LocalOnly3 --> EndFailed1
    LocalOnly4 --> EndFailed2
    
    SendAPI5 --> EndUnknown1[🏁 FIN ERREUR<br/>Exit Code: 3]
    SendAPI6 --> EndUnknown2[🏁 FIN ERREUR<br/>Exit Code: 3]
    LocalOnly5 --> EndUnknown1
    LocalOnly6 --> EndUnknown2
    
    %% ========== RÉSUMÉ DES CODES DE SORTIE ==========
    %% Exit Code 0: Succès complet
    %% Exit Code 2: Échec fonctionnel (tests, planning) OU erreur navigateur
    %% Exit Code 3: Erreur infrastructure (API, technique)
    
    %% ========== STYLING ==========
    classDef successClass fill:#d4edda,stroke:#28a745,stroke-width:3px,color:#155724
    classDef errorClass fill:#f8d7da,stroke:#dc3545,stroke-width:3px,color:#721c24
    classDef warningClass fill:#fff3cd,stroke:#ffc107,stroke-width:2px,color:#856404
    classDef processClass fill:#e2e3e5,stroke:#6c757d,stroke-width:2px,color:#495057
    classDef decisionClass fill:#cce5ff,stroke:#007bff,stroke-width:2px,color:#004085
    classDef criticalClass fill:#721c24,stroke:#ffffff,stroke-width:4px,color:#ffffff
    classDef infrastructureClass fill:#6f42c1,stroke:#ffffff,stroke-width:3px,color:#ffffff
    
    %% Succès
    class TestSuccess1,TestSuccess2,SetSuccess1,SetSuccess2,EndSuccess1,EndSuccess2 successClass
    
    %% Erreurs critiques (Exit immédiat)
    class ExitCritical1,ExitCritical2,ExitCritical3,ExitInfrastructure1,ExitInfrastructure2,ExitInfrastructure3,ExitInfrastructure4,ExitInfrastructure5 criticalClass
    class ExitPlanning1,ExitPlanning2,ExitPlanning3,ExitPlanning4,ExitBrowser1,ExitBrowser2 criticalClass
    
    %% Erreurs infrastructure
    class SetInfrastructureError1,SetInfrastructureError2,SetInfrastructureError3,SetInfrastructureError4,SetInfrastructureError5 infrastructureClass
    class SetBrowserError1,SetBrowserError2,SetTestError1,SetTestError2,EndUnknown1,EndUnknown2 infrastructureClass
    
    %% Erreurs fonctionnelles
    class TestFailed1,TestFailed2,SetFailed1,SetFailed2,EndFailed1,EndFailed2 errorClass
    class SetPlanningError1,SetPlanningError2,SetPlanningError3,SetPlanningError4 errorClass
    
    %% Warnings
    class WarnDirectories1,WarnDirectories2,NoPlanningData,LocalOnly1,LocalOnly2,LocalOnly3,LocalOnly4,LocalOnly5,LocalOnly6 warningClass
    
    %% Processus
    class Start,InitExecution,LoadEnvVars,ConfigLoaded,StoreAPIData,FinalizeConfigAPI,FinalizeConfigNoAPI processClass
    class Finalize1,Finalize2,Finalize3,Finalize4,Finalize5,Finalize6 processClass
    
    %% Décisions
    class CheckScenarioVar,LoadConfigFile,LoadCommonConfig,CheckCommonFile,CheckLectureMode,APIResult,PlanningResult decisionClass
    class DirectorySuccess1,DirectorySuccess2,CheckPlanningData,BrowserResult1,BrowserResult2,TestExecution1,TestExecution2 decisionClass
    class CheckInscription1,CheckInscription2,CheckInscription3,CheckInscription4,CheckInscription5,CheckInscription6 decisionClass
```
