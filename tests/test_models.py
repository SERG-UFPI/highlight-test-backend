import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Repository, AdditionalData, Pipeline, User
from app.enums import StatusEnum, UserStatusEnum
from app.schemas import LanguageEnum, StageEnum
from datetime import datetime
import uuid

class TestModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up an in-memory SQLite database
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_repository_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git",
            registration_date=datetime.now()
        )
        self.session.add(repo)
        self.session.commit()

        retrieved_repo = self.session.query(Repository).filter_by(owner="test_owner").first()
        self.assertIsNotNone(retrieved_repo)
        self.assertEqual(retrieved_repo.owner, "test_owner")
        self.assertEqual(retrieved_repo.default_branch, "main")

    def test_additional_data_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git",
            registration_date=datetime.now()
        )
        self.session.add(repo)
        self.session.commit()

        additional_data = AdditionalData(
            id=uuid.uuid4(),
            repository=repo.id,
            name="test_name",
            language=LanguageEnum.PYTHON,
            forks_count=10,
            open_issues_count=5
        )
        self.session.add(additional_data)
        self.session.commit()

        retrieved_data = self.session.query(AdditionalData).filter_by(name="test_name").first()
        self.assertIsNotNone(retrieved_data)
        self.assertEqual(retrieved_data.language, LanguageEnum.PYTHON)
        self.assertEqual(retrieved_data.forks_count, 10)

    def test_pipeline_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git",
            registration_date=datetime.now()
        )
        self.session.add(repo)
        self.session.commit()

        pipeline = Pipeline(
            id=uuid.uuid4(),
            repository=repo.id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS,
            share_consent=True
        )
        self.session.add(pipeline)
        self.session.commit()

        retrieved_pipeline = self.session.query(Pipeline).filter_by(stage=StageEnum.CLONE).first()
        self.assertIsNotNone(retrieved_pipeline)
        self.assertEqual(retrieved_pipeline.status, StatusEnum.IN_PROGRESS)
        self.assertTrue(retrieved_pipeline.share_consent)

    def test_user_model(self):
        user = User(
            id=uuid.uuid4(),
            username="test_user",
            hashed_password="hashed_password",
            fullname="Test User",
            email="test_user@example.com",
            status=UserStatusEnum.ACTIVE,
            github_user=True
        )
        self.session.add(user)
        self.session.commit()

        retrieved_user = self.session.query(User).filter_by(username="test_user").first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.fullname, "Test User")
        self.assertEqual(retrieved_user.status, UserStatusEnum.ACTIVE)

if __name__ == "__main__":
    unittest.main()