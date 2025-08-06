#!/usr/bin/bash
# qualite de code : shellcheck
# shellcheck enable=require-variable-braces # disable=SC2250
# script en mode strict
set -euo pipefail
#-----------------------------------------------------------------------------#
#                              simulateur_v6.sh                               #
#                                                                             #
# Script d'execution des scenarios PSN (simulateur v6) playwright/python.     #
# Version simplifiée  :                                                       #
# TOUS LES PARAMETRES SONT LUS A PARTIR DE L'ENVIRONNEMENT                    #
# Aucune utilisation de la ligne de commande                                  #
#                                                                             #
# TODO : Implementation de la rotation des adresses IP pour tests des DACS    #
#                                                                             #
# Change History                                                              #
# 19/05/2025 PSN-CT (M-O) simulateur_v6 V 0.0.1                               #
#-----------------------------------------------------------------------------#

# fonctions utilitaires:

# affiche une erreur sur sortie erreur
errorMsg() {
  echo -e "[Erreur] ${*}" >&2
}

# affiche une erreur et sort avec code erreur 1
die() {
  errorMsg "${*}"
  exit 1
}

# Controle des parametres et variables

# NOM_SCENARIO (obligatoire)
# PLATEFORME ou environnement (par defaut prod)
# TODO BIND : utilisation de la rotation des adresses IP (par defaut false)
# HEADLESS : le navigateur n'est pas affiché (par defaut true)

# export SCENARIO=bofip_archive_impots_consulter
[[ -z ${NOM_SCENARIO+x} ]] && die "NOM_SCENARIO non defini"

export PLATEFORME=${PLATEFORME:-prod}
export HEADLESS=${HEADLESS:-true}

export SIMU_PATH="${SIMU_PATH-/opt/simulateur_v6}"
echo "Chemin du simulateur = ${PLAYWRIGHT_BROWSER_PATH}"

export OUTPUT_PATH="${SIMU_OUTPUT-/var/simulateur_v6}"
export WORKSPACE="${WORKSPACE-/var/simulateur_v6/workspace/${NOM_SCENARIO}}"
echo "[/opt/simulateur_v6 | workspace ] = ${WORKSPACE}"

PLAYWRIGHT_BROWSER_PATH="${PLAYWRIGHT_BROWSER_PATH-${SIMU_PATH}/browsers}"
export PLAYWRIGHT_BROWSER_PATH
echo "Chemin des navigateurs = ${PLAYWRIGHT_BROWSER_PATH}"

# Activation des API's
export LECTURE=true
export INSCRIPTION=true

# Chemin des scénarios
export SCENARIOS_PATH="${SCENARIOS_PATH-/opt/scenarios_v6}"

# Nom de la VM Windows
export NOM_VM_WINDOWS="1 - Windows 11 POCv6 (.40)"

# Type de scénario
export TYPE_SCENARIO="${TYPE_SCENARIO-web}"

echo "[simulateur_v6.sh] Lancement du scénario : ${NOM_SCENARIO}"

source "${SIMU_PATH}/venv/bin/activate"
# /<chemain_simulateur_v6>/simulateur_v6/venv/bin/python playwright install
pytest "${SIMU_PATH}"/scenarios_python/"${NOM_SCENARIO}".py -x -s


echo "[simulateur_v6.sh] Fin de l'éxecution"