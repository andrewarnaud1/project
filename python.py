#!.env python3

import argparse
from datetime import datetime
import glob
import os
import pathlib
import pytest
import requests
import yaml
from simulateur.enums import Status
from simulateur.run_tests_via_yaml import TestAPI
from utils.utils import load_config_files
from utils.yaml_loader import load_yaml_file

URL_API = os.environ.get('URL_API', None)

def get_scenario_last_execution(identifiant: str):
    if not identifiant:
        return None
    if not URL_API:
        raise KeyError('url_api non défini')
    url = f"{URL_API}/injapi/last_execution/{identifiant}"
    try:
        response  = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None

        response_json = response.json()
        execution =  response_json.get('execution')
        if not execution:
            return None
        return execution.get('status', None)
    except Exception:
        print('impossible de récuperer le status de la dérnière execution du scenario')
        return None


def get_scenario_info_from_api(scenario_name):
    scenario_id = get_indentifiant_from_scenario_name(scenario_name)
    url = f"{URL_API}injapi/scenario/{scenario_id}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()
    return None


def get_json_execution(scenario_name: str):
    root_dir =  os.environ.get('SIMU_OUTPUT', '/tmp')
    lecture = os.environ.get('LECTURE', None).lower()
    if lecture == 'true':
        api_response = get_scenario_info_from_api(scenario_name)
        if api_response is None:
            return None
        root_dir = f"{root_dir}/{api_response.get('application').get('nom')}"
        scenario_name = api_response.get('nom')

    today_report_folder = f'{root_dir}/{scenario_name}/{datetime.now().date()}'
    last_report_folder = max(pathlib.Path(today_report_folder).glob('*/'), key=os.path.getmtime)
    json_path = f"{str(last_report_folder)}/scenario.json"
    return load_yaml_file(json_path)


def post_execution_result_in_isac(scenario_name: str, json_execution:dict = None):
    inscription = os.environ.get('INSCRIPTION', None).lower()

    if inscription == 'true':
        if not URL_API:
            print("la variable url_api n'est pas défini")
            return

        url = f"{URL_API}/injapi/scenario/execution"
        if json_execution is None:
            json_execution = get_json_execution(scenario_name)
        if json_execution is None:
            print("le fichier json des resultats de scenarion est introuvable")
            return

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/plain",
        }

        response = requests.post(url, headers=headers, timeout=10, json=json_execution)
        if response.status_code != 201:
            print("impossible de sauvgarder le resultat du scenarion dans isac")
            return
        print("sauvgarder le resultat du scenarion dans isac")


def get_indentifiant_from_scenario_name(scenario: str):
    work_dir = str(pathlib.Path().resolve())
    config_file = f"{work_dir}/config/scenarios/{scenario}.conf"
    configuration = load_yaml_file(config_file)
    return configuration.get('identifiant', None)

def run_generated_test(work_dir: str, scenario_name :str):
    file_path = f"{work_dir}/scenarios/python/{scenario_name}.py"
    result = pytest.main(["-x", "-s", file_path])

    if result != 0:
        scenario_id = get_indentifiant_from_scenario_name(scenario_name)
        if not scenario_id:
            raise KeyError("l'identifiant du test dans le fichier de configuration est introuvable!")
        last_execution_status = get_scenario_last_execution(scenario_id)
        if last_execution_status is None:
            return False
        if last_execution_status in [Status.SUCCESS.value, Status.WARNING.value]:
            print("re-lancer le scenario ")
            result = pytest.main(["-x", "-s", file_path])
            if result != 0:
                return False
    return result == 0

def run_exadata_test(work_dir: str, scenario_name: str):
    os.environ['chemin_images_exadata'] = f"{work_dir}/scenarios_exadata/images/{scenario_name}"
    file_path = f"{work_dir}/scenarios_exadata/{scenario_name}.py"
    result = pytest.main(["-x", "-s", file_path])
    return result == 0

def run_yaml_test(scenario_name: str, scenario_yaml : dict):
    scenario_config = load_config_files(scenario_name)
    test_api_runner = TestAPI(scenario_yaml, scenario_config)
    return test_api_runner.run()

def run_scenario(scenario_name: str, work_dir: str, exadata: bool = None):
    is_success = False
    json_execution = None
    scenario_yaml = None

    os.environ['SCENARIO'] = scenario_name

    if exadata:
        is_success = run_exadata_test(work_dir, scenario_name)

    else:
        yaml_file_path = f"scenarios/yaml/{scenario_name}.yaml"
        with open(yaml_file_path) as f:
            scenario_yaml = yaml.safe_load(f)

        if scenario_type := scenario_yaml.get('type'):
            if scenario_type == 'API': # todo we will add DNS, TELNET SMTP ...etc
                is_success, json_execution  = run_yaml_test(scenario_name, scenario_yaml)
        else:
            is_success = run_generated_test(work_dir, scenario_name)

    try:
        post_execution_result_in_isac(scenario_name, json_execution)
    except Exception as e:
        raise TimeoutError('impossible de sauvgarder le resultat dans ISAC!', str(e))
    return is_success

def run_multi_scenarios(scenarios_dir: str):
    failed_tests = []
    scenarios_files = glob.glob(f"{scenarios_dir}/*.py")
    for file_path in scenarios_files:
        scenario = file_path.split('/')[-1].split('.')[0]
        os.environ['SCENARIO'] = scenario
        result = pytest.main(["-x", "-s", file_path])
        if result == 0:
            print(f"{scenario} test: OK ✅")
        else:
            failed_tests.append(scenario)
            print(f"{scenario} test: KO ❌")
    print(f"failed tests {len(failed_tests)}", failed_tests)

def main():
    parser = argparse.ArgumentParser(description="scpript pour lancer les scénarios.")
    parser.add_argument("-s", "--scenario", required=False, help="Nom du scenario")
    parser.add_argument("-a", "--all", required=False, action="store_true",  help="tout les scenarios")
    parser.add_argument("-x", "--exadata", required=False, action="store_true",  help="exadata test")
    args = parser.parse_args()

    work_dir = str(pathlib.Path().resolve())
    if scenario := args.scenario:
        is_success = run_scenario(scenario, work_dir, args.exadata)
        if is_success:
            print(f"{scenario} test: OK ✅")
        else:
            print(f"{scenario} test: KO ❌")

    if args.all: # pour tester en local
        scenarios_dir = work_dir + "/scenarios/python"
        run_multi_scenarios(scenarios_dir)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("erreur lors de l'execution du scenarion", str(e))
