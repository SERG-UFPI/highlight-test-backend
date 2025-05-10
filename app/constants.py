import os

MY_SEPARATOR = "/"

PARENT_DIRECTORY = os.path.dirname(os.path.dirname(__file__))
BASE_RESULTS_PATH = os.path.join(PARENT_DIRECTORY, "results") + MY_SEPARATOR
BASE_PROJECTS = os.path.join(BASE_RESULTS_PATH, "projects") + MY_SEPARATOR
BASE_LOG_COMMITS = os.path.join(BASE_RESULTS_PATH, "commits_history") + MY_SEPARATOR
BASE_LOG_PERIOD_REVISIONS = os.path.join(BASE_RESULTS_PATH, "period_revisions") + MY_SEPARATOR
BASE_LOG_REVISIONS = os.path.join(BASE_RESULTS_PATH, "revisions") + MY_SEPARATOR
BASE_LOG_TEST_FILE = os.path.join(BASE_RESULTS_PATH, "testfile_history") + MY_SEPARATOR
BASE_LOG_LOC = os.path.join(BASE_RESULTS_PATH, "loc_history") + MY_SEPARATOR
BASE_LOG_CLOC = os.path.join(BASE_RESULTS_PATH, "cloc_data_history") + MY_SEPARATOR
BASE_LOG_PROJECT_DIMENSION = os.path.join(BASE_RESULTS_PATH, "project_dimension") + MY_SEPARATOR
BASE_LOG_MAINTENANCE_ACTIVITIES = os.path.join(BASE_RESULTS_PATH, "maintenance_activities") + MY_SEPARATOR
BASE_SUMMARY_MAINTENANCE_ACTIVITIES = os.path.join(BASE_RESULTS_PATH, "summary_activities") + MY_SEPARATOR
BASE_LOG_CO_EVOLUTION = os.path.join(BASE_RESULTS_PATH, "co_evolution_analysis") + MY_SEPARATOR

RESOURCES_DIR = os.path.join(PARENT_DIRECTORY, "app", "resources") + MY_SEPARATOR

EXTERNAL_DIR = os.path.join(PARENT_DIRECTORY, "external") + MY_SEPARATOR

TEST_CODE_CLASSIFICATION_DIR = os.path.join(PARENT_DIRECTORY, "app", "libs", "test_code_classification") + MY_SEPARATOR

FILE_EXTENSION_ACCEPTED = ["js","java","py","php","rb", "c", "cpp", "cs", "m", "clj", "go", "hs", "lua", "pl", "r", "rs", "scala", "sh", "swift", "tex", "vim"]

BASE_PROJECTS_FOLDER_NAME = "projects"

IMPORTED_PROJECTS_FOLDER_NAME = "projetos"

