import unittest
import json
from app.dtos.commit_maintenance_activities_result import CommitMaintenanceActivitiesResult

class TestCommitMaintenanceActivitiesResult(unittest.TestCase):

    def test_initialization(self):
        obj = CommitMaintenanceActivitiesResult()
        self.assertEqual(obj.hash, "")
        self.assertEqual(obj.message, "")
        self.assertEqual(obj.bug_fix_regex_count, 0)
        self.assertEqual(obj.adaptive_regex_count, 0)
        self.assertEqual(obj.adaptive_by_negation_regex_count, 0)
        self.assertEqual(obj.perfective_regex_count, 0)
        self.assertEqual(obj.refactor_regex_count, 0)
        self.assertEqual(obj.is_perfective, False)
        self.assertEqual(obj.is_refactor, False)
        self.assertEqual(obj.is_adaptive, 0)
        self.assertEqual(obj.is_adaptive_by_negation, False)
        self.assertEqual(obj.is_corrective, False)
        self.assertEqual(obj.perfective_in_text, "")
        self.assertEqual(obj.refactor_in_text, "")
        self.assertEqual(obj.adaptive_in_text, "")
        self.assertEqual(obj.adaptive_by_negation_in_text, "")
        self.assertEqual(obj.corrective_in_text, "")

    def test_set_from_csv(self):
        obj = CommitMaintenanceActivitiesResult()
        csv_row = [
            "1", "Test message", "5", "3", "2", "4", "6", "True", "False",
            "2", "False", "True", "Perfective text", "Refactor text",
            "Adaptive text", "Adaptive by negation text", "Corrective text"
        ]
        obj.set_from_csv(csv_row)
        self.assertEqual(obj.hash, "1")
        self.assertEqual(obj.message, "Test message")
        self.assertEqual(obj.bug_fix_regex_count, 5)
        self.assertEqual(obj.adaptive_regex_count, 3)
        self.assertEqual(obj.adaptive_by_negation_regex_count, 2)
        self.assertEqual(obj.perfective_regex_count, 4)
        self.assertEqual(obj.refactor_regex_count, 6)
        self.assertEqual(obj.is_perfective, True)
        self.assertEqual(obj.is_refactor, False)
        self.assertEqual(obj.is_adaptive, 2)
        self.assertEqual(obj.is_adaptive_by_negation, False)
        self.assertEqual(obj.is_corrective, True)
        self.assertEqual(obj.perfective_in_text, "Perfective text")
        self.assertEqual(obj.refactor_in_text, "Refactor text")
        self.assertEqual(obj.adaptive_in_text, "Adaptive text")
        self.assertEqual(obj.adaptive_by_negation_in_text, "Adaptive by negation text")
        self.assertEqual(obj.corrective_in_text, "Corrective text")

    def test_str_method(self):
        obj = CommitMaintenanceActivitiesResult()
        obj.hash = "1"
        obj.message = "Test message"
        expected_json = json.dumps({
            "hash": "1",
            "message": "Test message",
            "bug_fix_regex_count": 0,
            "adaptive_regex_count": 0,
            "adaptive_by_negation_regex_count": 0,
            "perfective_regex_count": 0,
            "refactor_regex_count": 0,
            "is_perfective": False,
            "is_refactor": False,
            "is_adaptive": 0,
            "is_adaptive_by_negation": False,
            "is_corrective": False,
            "perfective_in_text": "",
            "refactor_in_text": "",
            "adaptive_in_text": "",
            "adaptive_by_negation_in_text": "",
            "corrective_in_text": ""
        })
        self.assertEqual(str(obj), expected_json)

if __name__ == "__main__":
    unittest.main()