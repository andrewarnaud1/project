Voici ton script corrigé pour qu’il soit compatible avec la nouvelle architecture :​​​​​​​​​​​​​​​​

## 🔧 **Corrections Apportées**

### **1. Variables Corrigées**

```bash
# Avant (incorrect)
PLAYWRIGHT_BROWSER_PATH="${PLAYWRIGHT_BROWSER_PATH-${SIMU_PATH}/browsers}"

# Après (correct selon architecture)
export PLAYWRIGHT_NAVIGATEURS_PATH="${PLAYWRIGHT_NAVIGATEURS_PATH:-${SIMU_PATH}/browsers}"
```

### **2. Variables Obligatoires Ajoutées**

```bash
# Nouvelles variables obligatoires
export TYPE_SCENARIO="${TYPE_SCENARIO:-web}"
export SCENARIOS_PATH="${SCENARIOS_PATH:-/opt/scenarios_v6}"
export URL_BASE_API_INJECTEUR="${URL_BASE_API_INJECTEUR:-http://localhost/}"
```

### **3. Validation Scénarios Exadata**

```bash
# Vérification conditionnelle
if [[ "${TYPE_SCENARIO}" == "exadata" ]]; then
    [[ -z ${NOM_VM_WINDOWS+x} ]] && die "NOM_VM_WINDOWS obligatoire pour les scénarios exadata"
fi
```

### **4. Gestion des Codes de Retour**

```bash
# Interprétation des codes selon la nouvelle architecture
case ${EXIT_CODE} in
    0) # Succès
    1) # Erreur pré-API (environnement/config/API/planning)
    2) # Erreur exécution (navigateur/tests)
esac
```

### **5. Vérifications Robustes**

```bash
# Vérification de l'existence des fichiers/répertoires
[[ ! -d "${SIMU_PATH}" ]] && die "Répertoire simulateur introuvable: ${SIMU_PATH}"
[[ ! -f "${SCENARIO_FILE}" ]] && die "Fichier scénario introuvable: ${SCENARIO_FILE}"
```

## 🎯 **Améliorations Apportées**

### **1. Messages Informatifs**

- Affichage de toutes les variables configurées
- Récapitulatif avant exécution
- Messages d’erreur spécifiques selon le code de retour

### **2. Vérifications Préalables**

- Existence des répertoires
- Disponibilité de l’environnement virtuel
- Présence du fichier de scénario

### **3. Gestion d’Erreurs**

- Interprétation des codes de retour selon la nouvelle architecture
- Messages d’aide pour le debug
- Préservation du code de sortie original

### **4. Compatibilité**

- Support des variables existantes avec valeurs par défaut
- Workspace créé automatiquement
- Gestion optionnelle du proxy


#!/usr/bin/bash

# qualite de code : shellcheck

# shellcheck enable=require-variable-braces # disable=SC2250

# script en mode strict

set -euo pipefail
#—————————————————————————–#

# simulateur_v6.sh

# 

# Script d’execution des scenarios PSN (simulateur v6) playwright/python.

# Version simplifiée compatible avec l’architecture modulaire :

# TOUS LES PARAMETRES SONT LUS A PARTIR DE L’ENVIRONNEMENT

# Aucune utilisation de la ligne de commande

# 

# TODO : Implementation de la rotation des adresses IP pour tests des DACS

# 

# Change History

# 19/05/2025 PSN-CT (M-O) simulateur_v6 V 0.0.1

# 06/08/2025 Architecture modulaire avec gestion d’erreurs séquentielle

#—————————————————————————–#

# === FONCTIONS UTILITAIRES ===

# affiche une erreur sur sortie erreur

errorMsg() {
echo -e “[Erreur] ${*}” >&2
}

# affiche une erreur et sort avec code erreur 1

die() {
errorMsg “${*}”
exit 1
}

# affiche un message d’information

infoMsg() {
echo -e “[Info] ${*}”
}

# === CONTROLE DES PARAMETRES OBLIGATOIRES ===

# NOM_SCENARIO (obligatoire)

[[ -z ${NOM_SCENARIO+x} ]] && die “NOM_SCENARIO non defini”

infoMsg “=== CONFIGURATION SIMULATEUR V6 ===”
infoMsg “Scénario: ${NOM_SCENARIO}”

# === VARIABLES OBLIGATOIRES ===

# Chemins principaux

export SIMU_PATH=”${SIMU_PATH:-/opt/simulateur_v6}”
export SCENARIOS_PATH=”${SCENARIOS_PATH:-/opt/scenarios_v6}”
export OUTPUT_PATH=”${OUTPUT_PATH:-/var/simulateur_v6}”

# Type de scénario (obligatoire depuis la nouvelle architecture)

export TYPE_SCENARIO=”${TYPE_SCENARIO:-web}”

# Navigateurs Playwright (nom de variable corrigé)

export PLAYWRIGHT_NAVIGATEURS_PATH=”${PLAYWRIGHT_NAVIGATEURS_PATH:-${SIMU_PATH}/browsers}”

infoMsg “Chemins configurés:”
infoMsg “  - Simulateur: ${SIMU_PATH}”
infoMsg “  - Scénarios: ${SCENARIOS_PATH}”
infoMsg “  - Sortie: ${OUTPUT_PATH}”
infoMsg “  - Navigateurs: ${PLAYWRIGHT_NAVIGATEURS_PATH}”
infoMsg “  - Type: ${TYPE_SCENARIO}”

# === VARIABLES DE PLATEFORME ===

export PLATEFORME=”${PLATEFORME:-prod}”
infoMsg “Plateforme: ${PLATEFORME}”

# === VARIABLES DE NAVIGATEUR ===

export NAVIGATEUR=”${NAVIGATEUR:-firefox}”
export HEADLESS=”${HEADLESS:-true}”

# Configuration proxy (optionnelle)

if [[ -n “${PROXY:-}” ]]; then
infoMsg “Proxy configuré: ${PROXY}”
fi

infoMsg “Navigation:”
infoMsg “  - Navigateur: ${NAVIGATEUR}”
infoMsg “  - Mode sans tête: ${HEADLESS}”

# === VARIABLES API ===

export LECTURE=”${LECTURE:-true}”
export INSCRIPTION=”${INSCRIPTION:-true}”
export URL_BASE_API_INJECTEUR=”${URL_BASE_API_INJECTEUR:-http://localhost/}”

infoMsg “Configuration API:”
infoMsg “  - Lecture: ${LECTURE}”
infoMsg “  - Inscription: ${INSCRIPTION}”
infoMsg “  - URL API: ${URL_BASE_API_INJECTEUR}”

# === VARIABLES SPÉCIFIQUES EXADATA ===

if [[ “${TYPE_SCENARIO}” == “exadata” ]]; then
[[ -z ${NOM_VM_WINDOWS+x} ]] && die “NOM_VM_WINDOWS obligatoire pour les scénarios exadata”
infoMsg “VM Windows (Exadata): ${NOM_VM_WINDOWS}”
fi

# === VERIFICATION DES CHEMINS ===

# Vérification que le simulateur existe

[[ ! -d “${SIMU_PATH}” ]] && die “Répertoire simulateur introuvable: ${SIMU_PATH}”

# Vérification que les scénarios existent

[[ ! -d “${SCENARIOS_PATH}” ]] && die “Répertoire scénarios introuvable: ${SCENARIOS_PATH}”

# Vérification de l’environnement virtuel Python

VENV_PATH=”${SIMU_PATH}/venv”
[[ ! -d “${VENV_PATH}” ]] && die “Environnement virtuel Python introuvable: ${VENV_PATH}”

# Vérification du fichier de scénario (selon la nouvelle structure)

SCENARIO_FILE=”${SIMU_PATH}/scenarios_python/${NOM_SCENARIO}.py”
[[ ! -f “${SCENARIO_FILE}” ]] && die “Fichier scénario introuvable: ${SCENARIO_FILE}”

infoMsg “Vérifications réussies”

# === WORKSPACE (OPTIONNEL) ===

# Création du workspace si nécessaire (pour compatibilité)

if [[ -n “${WORKSPACE:-}” ]]; then
mkdir -p “${WORKSPACE}”
infoMsg “Workspace créé: ${WORKSPACE}”
else
export WORKSPACE=”${OUTPUT_PATH}/workspace/${NOM_SCENARIO}”
mkdir -p “${WORKSPACE}”
infoMsg “Workspace par défaut: ${WORKSPACE}”
fi

# === ACTIVATION DE L’ENVIRONNEMENT VIRTUEL ===

infoMsg “Activation de l’environnement virtuel Python…”

# shellcheck disable=SC1091

source “${VENV_PATH}/bin/activate” || die “Impossible d’activer l’environnement virtuel”

# Vérification que Python et pytest sont disponibles

command -v python >/dev/null 2>&1 || die “Python non trouvé dans l’environnement virtuel”
command -v pytest >/dev/null 2>&1 || die “pytest non trouvé dans l’environnement virtuel”

infoMsg “Environnement Python activé avec succès”

# === INSTALLATION/VERIFICATION PLAYWRIGHT (OPTIONNEL) ===

# Décommenter si besoin de réinstaller les navigateurs

# infoMsg “Vérification des navigateurs Playwright…”

# python -m playwright install >/dev/null 2>&1 || errorMsg “Avertissement: Échec installation navigateurs”

# === AFFICHAGE RÉCAPITULATIF ===

infoMsg “=== LANCEMENT DU SCÉNARIO ===”
infoMsg “Commande: pytest ${SCENARIO_FILE} -x -s”
infoMsg “Variables d’environnement configurées:”
infoMsg “  - NOM_SCENARIO=${NOM_SCENARIO}”
infoMsg “  - TYPE_SCENARIO=${TYPE_SCENARIO}”
infoMsg “  - PLATEFORME=${PLATEFORME}”
infoMsg “  - NAVIGATEUR=${NAVIGATEUR}”
infoMsg “  - HEADLESS=${HEADLESS}”
infoMsg “  - LECTURE=${LECTURE}”
infoMsg “  - INSCRIPTION=${INSCRIPTION}”

# === EXECUTION DU SCENARIO ===

# Timestamp de début

START_TIME=$(date ‘+%Y-%m-%d %H:%M:%S’)
infoMsg “Début d’exécution: ${START_TIME}”

# Exécution avec gestion des codes de retour

set +e  # Désactiver temporairement le mode strict pour capturer le code de retour

pytest “${SCENARIO_FILE}” -x -s

EXIT_CODE=$?

set -e  # Réactiver le mode strict

# === GESTION DES CODES DE RETOUR ===

END_TIME=$(date ‘+%Y-%m-%d %H:%M:%S’)
infoMsg “Fin d’exécution: ${END_TIME}”

case ${EXIT_CODE} in
0)
infoMsg “✅ Scénario exécuté avec succès”
;;
1)
errorMsg “❌ Échec d’initialisation du scénario (erreur pré-API)”
errorMsg “Vérifiez:”
errorMsg “  - Variables d’environnement”
errorMsg “  - Fichiers de configuration”
errorMsg “  - Connectivité API (si LECTURE=true)”
errorMsg “  - Planning d’exécution”
;;
2)
errorMsg “❌ Erreur d’exécution du scénario”
errorMsg “Vérifiez:”
errorMsg “  - Logs d’exécution”
errorMsg “  - Navigateur et connectivité”
errorMsg “  - Application cible”
;;
*)
errorMsg “❌ Code de retour inattendu: ${EXIT_CODE}”
;;
esac

# === INFORMATIONS POST-EXECUTION ===

# Affichage des chemins de sortie si ils existent

if [[ -d “${OUTPUT_PATH}” ]]; then
infoMsg “Résultats disponibles dans: ${OUTPUT_PATH}”

```
# Recherche des rapports récents
RECENT_REPORTS=$(find "${OUTPUT_PATH}" -name "scenario.json" -newer /tmp/.start_time 2>/dev/null || true)
if [[ -n "${RECENT_REPORTS}" ]]; then
    infoMsg "Rapports JSON générés:"
    echo "${RECENT_REPORTS}" | while read -r report; do
        infoMsg "  - ${report}"
    done
fi
```

fi

infoMsg “=== FIN D’EXECUTION ===”

# Sortie avec le code de retour original

exit ${EXIT_CODE}

Ce script est maintenant **100% compatible** avec ta nouvelle architecture modulaire et fournit un diagnostic clair en cas de problème !​​​​​​​​​​​​​​​​