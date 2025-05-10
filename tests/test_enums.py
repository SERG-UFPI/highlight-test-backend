import unittest
from app.enums import LanguageEnum, StageEnum, StatusEnum, UserStatusEnum

class TestEnums(unittest.TestCase):

    def test_language_enum(self):
        self.assertEqual(LanguageEnum.JAVASCRIPT.value, "JavaScript")
        self.assertEqual(LanguageEnum.JAVA.value, "Java")
        self.assertEqual(LanguageEnum.TYPESCRIPT.value, "TypeScript")
        self.assertEqual(LanguageEnum.PYTHON.value, "Python")
        self.assertEqual(LanguageEnum.CSHARP.value, "C#")
        self.assertEqual(LanguageEnum.PHP.value, "PHP")

    def test_stage_enum(self):
        self.assertEqual(StageEnum.CLONE.value, "Clone Repositories")
        self.assertEqual(StageEnum.EXTRACT_COMMITS.value, "Extract Commit Data")
        self.assertEqual(StageEnum.GENERATE_TIME_SERIES.value, "Generate Time Series")
        self.assertEqual(StageEnum.CALCULATE_METRICS.value, "Calculate Metrics")
        self.assertEqual(StageEnum.CO_EVOLUTION_ANALYSIS.value, "Co-evolution Analysis")

    def test_status_enum(self):
        self.assertEqual(StatusEnum.IN_PROGRESS.value, "In progress")
        self.assertEqual(StatusEnum.COMPLETED.value, "Completed")
        self.assertEqual(StatusEnum.ERROR.value, "Error")

    def test_user_status_enum(self):
        self.assertEqual(UserStatusEnum.ACTIVE.value, "Active")
        self.assertEqual(UserStatusEnum.BLOCKED.value, "Blocked")

if __name__ == "__main__":
    unittest.main()