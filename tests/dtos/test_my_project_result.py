import unittest
from app.dtos.my_project_result import MyProjectResult

class MockRow:
    def __init__(self, uses_external_id, external_id, name, full_name, language, forks_count, open_issues_count, created_at, pushed_at):
        self.uses_external_id = uses_external_id
        self.external_id = external_id
        self.name = name
        self.full_name = full_name
        self.language = language
        self.forks_count = forks_count
        self.open_issues_count = open_issues_count
        self.created_at = created_at
        self.pushed_at = pushed_at

class TestMyProjectResult(unittest.TestCase):

    def test_initialization_with_external_id(self):
        row = MockRow(
            uses_external_id=True,
            external_id="ext123",
            name="Test Project",
            full_name="test/test-project",
            language="Python",
            forks_count="10",
            open_issues_count="5",
            created_at="2023-01-01",
            pushed_at="2023-01-02"
        )
        obj = MyProjectResult(row, pipeline_id="pipeline123")
        self.assertEqual(obj.id, "ext123")
        self.assertEqual(obj.name, "Test Project")
        self.assertEqual(obj.base_git, "test/test-project")
        self.assertEqual(obj.project_language, "Python")
        self.assertEqual(obj.forks_count, 10)
        self.assertEqual(obj.open_issues_count, 5)
        self.assertEqual(obj.created_at, "2023-01-01")
        self.assertEqual(obj.pushed_at, "2023-01-02")

    def test_initialization_without_external_id(self):
        row = MockRow(
            uses_external_id=False,
            external_id="ext123",
            name="Test Project",
            full_name="test/test-project",
            language="Python",
            forks_count="10",
            open_issues_count="5",
            created_at="2023-01-01",
            pushed_at="2023-01-02"
        )
        obj = MyProjectResult(row, pipeline_id="pipeline123")
        self.assertEqual(obj.id, "pipeline123")
        self.assertEqual(obj.name, "Test Project")
        self.assertEqual(obj.base_git, "test/test-project")
        self.assertEqual(obj.project_language, "Python")
        self.assertEqual(obj.forks_count, 10)
        self.assertEqual(obj.open_issues_count, 5)
        self.assertEqual(obj.created_at, "2023-01-01")
        self.assertEqual(obj.pushed_at, "2023-01-02")

    def test_str_method(self):
        row = MockRow(
            uses_external_id=True,
            external_id="ext123",
            name="Test Project",
            full_name="test/test-project",
            language="Python",
            forks_count="10",
            open_issues_count="5",
            created_at="2023-01-01",
            pushed_at="2023-01-02"
        )
        obj = MyProjectResult(row, pipeline_id="pipeline123")
        self.assertEqual(str(obj), "ext123\nTest Project\n")

if __name__ == "__main__":
    unittest.main()