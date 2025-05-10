import unittest
from unittest.mock import MagicMock
from pydantic import HttpUrl
from app import models, schemas
from app.crud import (
    get_repository_by_id,
    get_repository_by_clone_url,
    create_repository,
    update_repository,
    delete_repository,
)
from datetime import datetime
from uuid import uuid4


class TestCRUD(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()

    def test_create_repository(self):
        repo_data = schemas.RepositoryCreate(default_branch="main", clone_url=HttpUrl("https://example.com/new_repo.git"))
        username = "testuser"
        mock_repo = models.Repository(**repo_data.dict(), owner=username, id=uuid4(), registration_date=datetime.now())
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_repo

        result = create_repository(self.db, repo_data, username)
        self.assertEqual(result.owner, username)
        self.assertEqual(str(result.clone_url), str(repo_data.clone_url))  # Comparação ajustada


    def test_delete_repository(self):
        self.db.query.return_value.filter.return_value.delete.return_value = 1
        result = delete_repository(self.db, "123")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()