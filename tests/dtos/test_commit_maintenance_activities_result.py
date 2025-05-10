import unittest
import json
from app.dtos.commit_maintenance_activities_result import CommitMaintenanceActivitiesResult

class TestCommitMaintenanceActivitiesResult(unittest.TestCase):

    def test_initialization(self):
        obj = CommitMaintenanceActivitiesResult()
        self.assertEqual(obj.id, "")
        self.assertEqual(obj.message, "")
        self.assertEqual(obj.bug_fix_regex_count, "")
        self.assertEqual(obj.adaptive_regex_count, "")
        self.assertEqual(obj.adaptive_by_negation_regex_count, "")
        self.assertEqual(obj.perfective_regex_count, "")
        self.assertEqual(obj.refactor_regex_count, "")
        self.assertEqual(obj.is_perfective, "")
        self.assertEqual(obj.is_refactor, "")
        self.assertEqual(obj.is_adaptive, "")
        self.assertEqual(obj.is_adaptive_by_negation, "")
        self.assertEqual(obj.is_corrective, "")
        self.assertEqual(obj.perfective_in_text, "")
        self.assertEqual(obj.refactor_in_text, "")
        self.assertEqual(obj.adaptive_in_text, "")
        self.assertEqual(obj.adaptive_by_negation_in_text, "")
        self.assertEqual(obj.corretive_in_text, "")

    def test_set_from_csv(self):
        obj = CommitMaintenanceActivitiesResult()
        csv_row = [
            "1", "Test message", "5", "3", "2", "4", "6", "True", "False",
            "True", "False", "True", "Perfective text", "Refactor text",
            "Adaptive text", "Adaptive by negation text", "Corrective text"
        ]
        obj.set_from_csv(csv_row)
        self.assertEqual(obj.id, "1")
        self.assertEqual(obj.message, "Test message")
        self.assertEqual(obj.bug_fix_regex_count, "5")
        self.assertEqual(obj.adaptive_regex_count, "3")
        self.assertEqual(obj.adaptive_by_negation_regex_count, "2")
        self.assertEqual(obj.perfective_regex_count, "4")
        self.assertEqual(obj.refactor_regex_count, "6")
        self.assertEqual(obj.is_perfective, "True")
        self.assertEqual(obj.is_refactor, "False")
        self.assertEqual(obj.is_adaptive, "True")
        self.assertEqual(obj.is_adaptive_by_negation, "False")
        self.assertEqual(obj.is_corrective, "True")
        self.assertEqual(obj.perfective_in_text, "Perfective text")
        self.assertEqual(obj.refactor_in_text, "Refactor text")
        self.assertEqual(obj.adaptive_in_text, "Adaptive text")
        self.assertEqual(obj.adaptive_by_negation_in_text, "Adaptive by negation text")
        self.assertEqual(obj.corretive_in_text, "Corrective text")

    def test_str_method(self):
        obj = CommitMaintenanceActivitiesResult()
        obj.id = "1"
        obj.message = "Test message"
        expected_json = json.dumps({
            "id": "1",
            "message": "Test message",
            "bug_fix_regex_count": "",
            "adaptive_regex_count": "",
            "adaptive_by_negation_regex_count": "",
            "perfective_regex_count": "",
            "refactor_regex_count": "",
            "is_perfective": "",
            "is_refactor": "",
            "is_adaptive": "",
            "is_adaptive_by_negation": "",
            "is_corrective": "",
            "perfective_in_text": "",
            "refactor_in_text": "",
            "adaptive_in_text": "",
            "adaptive_by_negation_in_text": "",
            "corretive_in_text": ""
        })
        self.assertEqual(str(obj), expected_json)

if __name__ == "__main__":
    unittest.main()