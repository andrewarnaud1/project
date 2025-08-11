classDiagram
%% Core Classes
class Scenario {
+str name
+Config config
+Browser browser
+ApiClient api_client
+Reporter reporter
+List[Step] steps
+List[Step] completed_steps
+int step_counter
+datetime start_time
+int status
+str comment
+str hostname
+str ip_address

```
    +create_step(name: str) Step
    +add_completed_step(step: Step)
    +finalize()
    +_generate_report() dict
    +_save_to_api()
}

class Step {
    +str name
    +int order
    +Scenario scenario
    +datetime start_time
    +float duration
    +int status
    +str comment
    +str url
    +List[str] screenshots
    +int _screenshot_counter
    
    +take_screenshot(page: Page, error: bool) str
    +success(message: str)
    +warning(message: str)
    +error(message: str)
    +_finalize()
    +to_dict() dict
}

class ScenarioBuilder {
    <<static>>
    +create_from_config() Scenario
}

class Browser {
    +Page page
    +BrowserContext context
    +str browser_type
    +dict options
    
    +launch()
    +new_page() Page
    +close()
}

%% Configuration Classes
class Config {
    +str scenario_name
    +str scenario_id
    +str platform
    +str browser_name
    +bool headless
    +str proxy
    +str scenarios_path
    +str output_path
    +str screenshot_dir
    +str report_dir
    +bool api_enabled
    +str api_base_url
    +bool generate_har
    +dict user
}

class ConfigLoader {
    <<static>>
    +load() Config
    +_load_env_config() dict
    +_load_yaml_config(env_config: dict) dict
    +_load_api_data(env_config: dict, yaml_config: dict) dict
    +_post_process_config(config: Config)
    +_load_user_data(config: Config) dict
}

class EnvLoader {
    <<static>>
    +load_environment_variables() dict
    +validate_required_vars(vars: dict)
}

class YamlLoader {
    <<static>>
    +load_yaml_file(filepath: str) dict
    +load_scenario_config(scenario_name: str, scenarios_path: str) dict
    +load_common_config(common_name: str, scenarios_path: str) dict
}

class ConfigValidator {
    +validate_config(config: Config) bool
    +validate_paths(config: Config) bool
    +validate_browser_config(config: Config) bool
    +validate_api_config(config: Config) bool
}

%% API Classes
class ApiClient {
    +str base_url
    +dict headers
    +int timeout
    
    +load_scenario_data(scenario_id: str) dict
    +save_execution_results(report_data: dict)
    +load_last_execution(scenario_id: str) dict
    +_make_request(method: str, endpoint: str, data: dict) dict
}

class ApiModels {
    +ScenarioData scenario_data
    +ExecutionResult execution_result
    +PlanningData planning_data
}

class ApiException {
    +str message
    +int status_code
    +dict response_data
}

%% Actions Classes
class WebActions {
    +Page page
    +Step step
    
    +click(locator, timeout: int)
    +fill(locator, value: str, timeout: int)
    +verify(locator, timeout: int)
    +wait_for_element(locator, timeout: int)
    +navigate_to(url: str)
}

class BaseActions {
    <<abstract>>
    +Page page
    +Step step
    
    +take_screenshot_on_error(exception: Exception)
    +log_action(action_name: str, details: str)
    +wait_and_verify(locator, timeout: int)
}

class ExadataActions {
    +Page page
    +Step step
    +str images_path
    
    +click_image(image_path: str, confidence: float)
    +type_in_field(image_path: str, text: str)
    +verify_image_exists(image_path: str, timeout: int)
    +wait_for_image(image_path: str, timeout: int)
}

%% Reporting Classes
class Reporter {
    +Config config
    +str screenshot_dir
    +str report_dir
    
    +take_screenshot(step: Step, page: Page, error: bool, screenshot_number: int) str
    +generate_json_report(scenario: Scenario) dict
    +generate_html_report(scenario: Scenario) str
    +save_report(report_data: dict, format: str)
}

class ScreenshotManager {
    +Config config
    +str base_path
    
    +capture_screenshot(page: Page, filename: str, full_page: bool) str
    +add_annotations(page: Page, title: str, timestamp: str)
    +blur_elements(page: Page, elements: List)
    +add_cursor_pointer(page: Page, element)
    +cleanup_annotations(page: Page)
}

class ReportModels {
    +ExecutionReport execution_report
    +StepReport step_report
    +ScreenshotInfo screenshot_info
}

%% Exadata Classes
class VisionEngine {
    +float confidence_threshold
    +str temp_screenshot_path
    
    +find_image_coordinates(template_path: str, screenshot_path: str) tuple
    +find_all_image_coordinates(template_path: str, screenshot_path: str) List[tuple]
    +take_screenshot_for_analysis(page: Page) str
    +compare_images(template: str, screenshot: str, confidence: float) bool
}

class ExadataModels {
    +ImageLocation image_location
    +ClickAction click_action
    +TypeAction type_action
}

%% Scheduling Classes
class PlanningChecker {
    +dict planning_data
    +bool holiday_checking_enabled
    
    +verify_execution_allowed(planning_data: dict) bool
    +check_time_slots(current_time: datetime, time_slots: List) bool
    +check_holidays(current_date: date, holiday_flag: bool) bool
}

class TimeSlotManager {
    +extract_time_slots_for_day(planning: List, day_number: int) List
    +validate_time_slot_format(slot: dict) bool
    +is_time_in_slot(current_time: time, slot: dict) bool
}

class HolidayManager {
    +is_holiday(date: datetime) bool
    +verify_holiday_flag(holiday_flag: bool, is_holiday: bool)
    +load_holiday_data(year: int) dict
}

%% Security Classes
class UserManager {
    +Config config
    +str users_path
    
    +load_user_data(user_file: str, platform: str) dict
    +decrypt_user_credentials(encrypted_data: dict) dict
    +get_user_for_scenario(scenario_config: dict) dict
}

class CryptoManager {
    +decrypt_aes_gcm(encrypted_data: dict) str
    +encrypt_aes_gcm(plaintext: str, key: str) dict
    +generate_key() str
    +validate_encrypted_format(data: dict) bool
}

%% Utility Classes
class FileUtils {
    <<static>>
    +ensure_directory_exists(path: str)
    +load_yaml_file(filepath: str) dict
    +save_json_file(data: dict, filepath: str)
    +get_file_extension(filepath: str) str
}

class TimeUtils {
    <<static>>
    +get_current_timestamp() str
    +format_duration(seconds: float) str
    +parse_time_string(time_str: str) time
    +is_time_in_range(current: time, start: time, end: time) bool
}

class ContextUtils {
    <<static>>
    +get_current_method_name(self_obj) str
    +get_call_stack() List[str]
    +format_context_info(method_name: str, params: dict) str
}

class Constants {
    <<static>>
    +SCENARIO_TYPES: List[str]
    +BROWSER_TYPES: List[str]
    +PLATFORMS: List[str]
    +STATUS_CODES: dict
    +DEFAULT_TIMEOUTS: dict
}

%% Fixtures Classes
class ScenarioFixtures {
    <<pytest fixture>>
    +scenario() Scenario
    +config() Config
    +browser() Browser
}

class StepFixtures {
    <<pytest fixture>>
    +step(scenario: Scenario, request) Step
    +page(browser: Browser) Page
}

class ConfigFixtures {
    <<pytest fixture>>
    +test_config() Config
    +mock_api_client() ApiClient
    +temp_directories() dict
}

%% Relationships
Scenario ||--o{ Step : contains
Scenario ||--|| Config : uses
Scenario ||--|| Browser : uses
Scenario ||--o| ApiClient : uses
Scenario ||--|| Reporter : uses

Step ||--|| Scenario : belongs_to
Step ||--o{ ScreenshotManager : uses_for_screenshots

ScenarioBuilder ..> Scenario : creates
ScenarioBuilder ..> ConfigLoader : uses
ScenarioBuilder ..> Browser : creates

ConfigLoader ..> Config : creates
ConfigLoader ..> EnvLoader : uses
ConfigLoader ..> YamlLoader : uses
ConfigLoader ..> ApiClient : uses
ConfigLoader ..> ConfigValidator : uses

WebActions ||--|| Step : uses
WebActions ||--|| Page : uses
BaseActions <|-- WebActions : extends
BaseActions <|-- ExadataActions : extends

ExadataActions ||--|| VisionEngine : uses

Reporter ||--|| ScreenshotManager : uses
Reporter ||--|| Config : uses

ApiClient ||--|| ApiModels : uses
ApiClient ..> ApiException : throws

PlanningChecker ||--|| TimeSlotManager : uses
PlanningChecker ||--|| HolidayManager : uses

UserManager ||--|| CryptoManager : uses
UserManager ||--|| Config : uses

VisionEngine ||--|| ExadataModels : uses

%% Fixture Dependencies
ScenarioFixtures ..> ScenarioBuilder : uses
StepFixtures ..> Scenario : uses
ConfigFixtures ..> ConfigLoader : uses
```