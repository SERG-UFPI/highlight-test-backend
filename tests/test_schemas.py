import unittest
from pydantic import ValidationError

from app.enums import StageEnum, StatusEnum
from app.schemas import (
    RepositoryCreate, RepositoryUpdate, AdditionalDataCreate, AdditionalDataUpdate,
    PipelineCreate, PipelineUpdate, UserCreate, UserUpdate, TermBase
)
from uuid import uuid4

class TestSchemas(unittest.TestCase):

    def test_repository_create_valid(self):
        data = {
            "default_branch": "main",
            "clone_url": "https://example.com/repo.git"
        }
        schema = RepositoryCreate(**data)
        self.assertEqual(schema.default_branch, "main")
        self.assertIsNotNone(schema.clone_url)

    def test_repository_create_invalid_url(self):
        data = {
            "default_branch": "main",
            "clone_url": "invalid_url"
        }
        with self.assertRaises(ValidationError):
            RepositoryCreate(**data)

    def test_additional_data_create_valid(self):
        data = {
            "repository": uuid4(),
            "name": "Test Repo",
            "language": "Python",
            "forks_count": 10,
            "open_issues_count": 5
        }
        schema = AdditionalDataCreate(**data)
        self.assertEqual(schema.name, "Test Repo")
        self.assertEqual(schema.language, "Python")

    def test_pipeline_create_valid(self):
        data = {
            "repository": uuid4(),
            "stage": StageEnum.CLONE,
            "status": StatusEnum.IN_PROGRESS
        }
        schema = PipelineCreate(**data)
        self.assertEqual(schema.stage, StageEnum.CLONE)
        self.assertEqual(schema.status, StatusEnum.IN_PROGRESS)

    def test_user_create_valid(self):
        data = {
            "username": "testuser",
            "password": "password123",
            "confirm_password": "password123",
            "fullname": "Test User",
            "email": "testuser@example.com"
        }
        schema = UserCreate(**data)
        self.assertEqual(schema.username, "testuser")
        self.assertEqual(schema.confirm_password, "password123")

    def test_term_base_valid(self):
        data = {
            "repository_id": str(uuid4()),
            "pipeline_id": str(uuid4()),
            "share_consent": True
        }
        schema = TermBase(**data)
        self.assertTrue(schema.share_consent)

if __name__ == "__main__":
    unittest.main()