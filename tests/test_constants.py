import unittest
from app.constants import (
    MY_SEPARATOR,
    PARENT_DIRECTORY,
    BASE_RESULTS_PATH,
    BASE_PROJECTS,
    BASE_LOG_COMMITS,
    BASE_LOG_PERIOD_REVISIONS,
    BASE_LOG_REVISIONS,
    BASE_LOG_TEST_FILE,
    BASE_LOG_LOC,
    BASE_LOG_CLOC,
    BASE_LOG_PROJECT_DIMENSION,
    BASE_LOG_MAINTENANCE_ACTIVITIES,
    BASE_SUMMARY_MAINTENANCE_ACTIVITIES,
    BASE_LOG_CO_EVOLUTION,
    RESOURCES_DIR,
    EXTERNAL_DIR,
    TEST_CODE_CLASSIFICATION_DIR,
    FILE_EXTENSION_ACCEPTED,
    BASE_PROJECTS_FOLDER_NAME,
    IMPORTED_PROJECTS_FOLDER_NAME
)

class TestConstants(unittest.TestCase):

    def test_constants_are_not_none(self):
        self.assertIsNotNone(MY_SEPARATOR)
        self.assertIsNotNone(PARENT_DIRECTORY)
        self.assertIsNotNone(BASE_RESULTS_PATH)
        self.assertIsNotNone(BASE_PROJECTS)
        self.assertIsNotNone(BASE_LOG_COMMITS)
        self.assertIsNotNone(BASE_LOG_PERIOD_REVISIONS)
        self.assertIsNotNone(BASE_LOG_REVISIONS)
        self.assertIsNotNone(BASE_LOG_TEST_FILE)
        self.assertIsNotNone(BASE_LOG_LOC)
        self.assertIsNotNone(BASE_LOG_CLOC)
        self.assertIsNotNone(BASE_LOG_PROJECT_DIMENSION)
        self.assertIsNotNone(BASE_LOG_MAINTENANCE_ACTIVITIES)
        self.assertIsNotNone(BASE_SUMMARY_MAINTENANCE_ACTIVITIES)
        self.assertIsNotNone(BASE_LOG_CO_EVOLUTION)
        self.assertIsNotNone(RESOURCES_DIR)
        self.assertIsNotNone(EXTERNAL_DIR)
        self.assertIsNotNone(TEST_CODE_CLASSIFICATION_DIR)
        self.assertIsNotNone(FILE_EXTENSION_ACCEPTED)
        self.assertIsNotNone(BASE_PROJECTS_FOLDER_NAME)
        self.assertIsNotNone(IMPORTED_PROJECTS_FOLDER_NAME)

if __name__ == "__main__":
    unittest.main()