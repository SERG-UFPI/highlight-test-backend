import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import *
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
        self.assertEqual(retrieved_repo.clone_url, "https://example.com/repo.git")

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
            full_name="test_owner/test_name",
            language=LanguageEnum.PYTHON,
            forks_count=10,
            open_issues_count=5,
            external_id="12345",
            uses_external_id=True
        )
        self.session.add(additional_data)
        self.session.commit()

        retrieved_data = self.session.query(AdditionalData).filter_by(name="test_name").first()
        self.assertIsNotNone(retrieved_data)
        self.assertEqual(retrieved_data.language, LanguageEnum.PYTHON)
        self.assertEqual(retrieved_data.forks_count, 10)
        self.assertEqual(retrieved_data.full_name, "test_owner/test_name")
        self.assertEqual(retrieved_data.external_id, "12345")
        self.assertTrue(retrieved_data.uses_external_id)

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
            share_consent=False
        )
        self.session.add(pipeline)
        self.session.commit()

        retrieved_pipeline = self.session.query(Pipeline).filter_by(stage=StageEnum.CLONE).first()
        self.assertIsNotNone(retrieved_pipeline)
        self.assertEqual(retrieved_pipeline.status, StatusEnum.IN_PROGRESS)
        self.assertFalse(retrieved_pipeline.share_consent)

    def test_user_model(self):
        user = User(
            id=uuid.uuid4(),
            username="test_user",
            hashed_password="hashed_password",
            fullname="Test User",
            email="test_user@example.com",
            status=UserStatusEnum.ACTIVE,
            github_user=True,
            github_token="gh_token123"
        )
        self.session.add(user)
        self.session.commit()

        retrieved_user = self.session.query(User).filter_by(username="test_user").first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.fullname, "Test User")
        self.assertEqual(retrieved_user.email, "test_user@example.com")
        self.assertEqual(retrieved_user.status, UserStatusEnum.ACTIVE)
        self.assertTrue(retrieved_user.github_user)
        self.assertEqual(retrieved_user.github_token, "gh_token123")

    def test_commit_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git"
        )
        self.session.add(repo)
        self.session.commit()

        pipeline = Pipeline(
            id=uuid.uuid4(),
            repository=repo.id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS
        )
        self.session.add(pipeline)
        self.session.commit()

        commit = Commit(
            id=uuid.uuid4(),
            hash="abc123def456",
            author_name="Test Author",
            committer_name="Test Committer",
            author_date=datetime.now(),
            message="Test commit message",
            pipeline_id=pipeline.id
        )
        self.session.add(commit)
        self.session.commit()

        retrieved_commit = self.session.query(Commit).filter_by(hash="abc123def456").first()
        self.assertIsNotNone(retrieved_commit)
        self.assertEqual(retrieved_commit.author_name, "Test Author")
        self.assertEqual(retrieved_commit.committer_name, "Test Committer")
        self.assertEqual(retrieved_commit.message, "Test commit message")

    def test_competence_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git"
        )
        self.session.add(repo)
        self.session.commit()

        pipeline = Pipeline(
            id=uuid.uuid4(),
            repository=repo.id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS
        )
        self.session.add(pipeline)
        self.session.commit()

        competence = Competence(
            id=uuid.uuid4(),
            competence="Python Programming",
            pipeline_id=pipeline.id
        )
        self.session.add(competence)
        self.session.commit()

        retrieved_competence = self.session.query(Competence).filter_by(competence="Python Programming").first()
        self.assertIsNotNone(retrieved_competence)
        self.assertEqual(retrieved_competence.competence, "Python Programming")

    def test_base_item_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git"
        )
        self.session.add(repo)
        self.session.commit()

        pipeline = Pipeline(
            id=uuid.uuid4(),
            repository=repo.id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS
        )
        self.session.add(pipeline)
        self.session.commit()

        base_item = BaseItem(
            id=uuid.uuid4(),
            base_item="Core Functionality",
            pipeline_id=pipeline.id
        )
        self.session.add(base_item)
        self.session.commit()

        retrieved_item = self.session.query(BaseItem).filter_by(base_item="Core Functionality").first()
        self.assertIsNotNone(retrieved_item)
        self.assertEqual(retrieved_item.base_item, "Core Functionality")

    def test_test_data_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git"
        )
        self.session.add(repo)
        self.session.commit()

        pipeline = Pipeline(
            id=uuid.uuid4(),
            repository=repo.id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS
        )
        self.session.add(pipeline)
        self.session.commit()

        test_data = TestData(
            id=uuid.uuid4(),
            file_path="src/test_file.py",
            is_test_file=True,
            has_test_import=True,
            has_test_call=True,
            pipeline_id=pipeline.id,
            commit_order=1
        )
        self.session.add(test_data)
        self.session.commit()

        retrieved_test_data = self.session.query(TestData).filter_by(file_path="src/test_file.py").first()
        self.assertIsNotNone(retrieved_test_data)
        self.assertTrue(retrieved_test_data.is_test_file)
        self.assertTrue(retrieved_test_data.has_test_import)
        self.assertTrue(retrieved_test_data.has_test_call)
        self.assertEqual(retrieved_test_data.commit_order, 1)

    def test_code_metrics_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git"
        )
        self.session.add(repo)
        self.session.commit()

        pipeline = Pipeline(
            id=uuid.uuid4(),
            repository=repo.id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS
        )
        self.session.add(pipeline)
        self.session.commit()

        code_metrics = CodeMetrics(
            id=uuid.uuid4(),
            full_name="test_owner/repo",
            timeseries={"commit1": {"loc": 100}, "commit2": {"loc": 120}},
            metric_type="production",
            pipeline_id=pipeline.id
        )
        self.session.add(code_metrics)
        self.session.commit()

        retrieved_metrics = self.session.query(CodeMetrics).filter_by(full_name="test_owner/repo").first()
        self.assertIsNotNone(retrieved_metrics)
        self.assertEqual(retrieved_metrics.metric_type, "production")
        self.assertEqual(retrieved_metrics.timeseries["commit1"]["loc"], 100)
        self.assertEqual(retrieved_metrics.timeseries["commit2"]["loc"], 120)

    def test_project_dimension_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git"
        )
        self.session.add(repo)
        self.session.commit()

        pipeline = Pipeline(
            id=uuid.uuid4(),
            repository=repo.id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS
        )
        self.session.add(pipeline)
        self.session.commit()

        project_dimension = ProjectDimension(
            id=uuid.uuid4(),
            n_commits=50,
            n_devs=5,
            n_forks_count=10,
            n_open_issues_count=15,
            pipeline_id=pipeline.id
        )
        self.session.add(project_dimension)
        self.session.commit()

        retrieved_dimension = self.session.query(ProjectDimension).filter_by(n_commits=50).first()
        self.assertIsNotNone(retrieved_dimension)
        self.assertEqual(retrieved_dimension.n_devs, 5)
        self.assertEqual(retrieved_dimension.n_forks_count, 10)
        self.assertEqual(retrieved_dimension.n_open_issues_count, 15)

    def test_commit_message_item_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git"
        )
        self.session.add(repo)
        self.session.commit()

        pipeline = Pipeline(
            id=uuid.uuid4(),
            repository=repo.id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS
        )
        self.session.add(pipeline)
        self.session.commit()

        commit_message_item = CommitMessageItem(
            id=uuid.uuid4(),
            hash="abc123def456",
            message="fix: issue with authentication",
            bug_fix_regex_count=1,
            adaptive_regex_count=0,
            adaptive_by_negation_regex_count=0,
            perfective_regex_count=0,
            refactor_regex_count=0,
            is_perfective=False,
            is_refactor=False,
            is_adaptive=False,
            is_adaptive_by_negation=False,
            is_corrective=True,
            corrective_in_text={"matches": ["fix", "issue"]},
            pipeline_id=pipeline.id
        )
        self.session.add(commit_message_item)
        self.session.commit()

        retrieved_item = self.session.query(CommitMessageItem).filter_by(hash="abc123def456").first()
        self.assertIsNotNone(retrieved_item)
        self.assertEqual(retrieved_item.message, "fix: issue with authentication")
        self.assertEqual(retrieved_item.bug_fix_regex_count, 1)
        self.assertTrue(retrieved_item.is_corrective)
        self.assertEqual(retrieved_item.corrective_in_text["matches"], ["fix", "issue"])

    def test_maintenance_activity_summary_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git"
        )
        self.session.add(repo)
        self.session.commit()

        pipeline = Pipeline(
            id=uuid.uuid4(),
            repository=repo.id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS
        )
        self.session.add(pipeline)
        self.session.commit()

        maintenance_summary = MaintenanceActivitySummary(
            id=uuid.uuid4(),
            n_corrective=25.5,
            n_adaptive=30.0,
            n_perfective=40.5,
            n_multi=4.0,
            pipeline_id=pipeline.id
        )
        self.session.add(maintenance_summary)
        self.session.commit()

        retrieved_summary = self.session.query(MaintenanceActivitySummary).first()
        self.assertIsNotNone(retrieved_summary)
        self.assertEqual(retrieved_summary.n_corrective, 25.5)

    def test_correlation_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git"
        )
        self.session.add(repo)
        self.session.commit()

        pipeline = Pipeline(
            id=uuid.uuid4(),
            repository=repo.id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS
        )
        self.session.add(pipeline)
        self.session.commit()

        correlation = Correlation(
            id=uuid.uuid4(),
            pearson_correlation=0.85,
            pipeline_id=pipeline.id
        )
        self.session.add(correlation)
        self.session.commit()

        retrieved_correlation = self.session.query(Correlation).filter_by(pearson_correlation=0.85).first()
        self.assertIsNotNone(retrieved_correlation)
        self.assertEqual(retrieved_correlation.pearson_correlation, 0.85)

    def test_code_distribution_detail_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git"
        )
        self.session.add(repo)
        self.session.commit()

        pipeline = Pipeline(
            id=uuid.uuid4(),
            repository=repo.id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS
        )
        self.session.add(pipeline)
        self.session.commit()

        code_detail = CodeDistributionDetail(
            id=uuid.uuid4(),
            path="src/main.py",
            loc=150,
            commit_order=3,
            language="Python",
            pipeline_id=pipeline.id
        )
        self.session.add(code_detail)
        self.session.commit()

        retrieved_detail = self.session.query(CodeDistributionDetail).filter_by(path="src/main.py").first()
        self.assertIsNotNone(retrieved_detail)
        self.assertEqual(retrieved_detail.loc, 150)
        self.assertEqual(retrieved_detail.commit_order, 3)
        self.assertEqual(retrieved_detail.language, "Python")

    def test_insights_model(self):
        repo = Repository(
            id=uuid.uuid4(),
            owner="test_owner",
            default_branch="main",
            clone_url="https://example.com/repo.git"
        )
        self.session.add(repo)
        self.session.commit()

        pipeline = Pipeline(
            id=uuid.uuid4(),
            repository=repo.id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS
        )
        self.session.add(pipeline)
        self.session.commit()

        insight = Insights(
            id=uuid.uuid4(),
            generated_text="This project shows good test coverage and modular design.",
            pipeline_id=pipeline.id
        )
        self.session.add(insight)
        self.session.commit()

        retrieved_insight = self.session.query(Insights).first()
        self.assertIsNotNone(retrieved_insight)
        self.assertEqual(retrieved_insight.generated_text,
                         "This project shows good test coverage and modular design.")

if __name__ == "__main__":
    unittest.main()