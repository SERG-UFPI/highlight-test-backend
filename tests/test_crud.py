import unittest
from unittest.mock import MagicMock
from uuid import uuid4
from pydantic import HttpUrl
from app.crud import *
from app.enums import UserStatusEnum, StatusEnum, StageEnum

class TestCRUD(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()

    # Repository tests
    def test_repository_by_id_returns_correct_repository(self):
        repository_id = "repo_123"
        mock_repository = models.Repository(id=repository_id, owner="testuser")
        self.db.query.return_value.filter.return_value.first.return_value = mock_repository

        result = get_repository_by_id(self.db, repository_id)
        self.assertEqual(result.id, repository_id)
        self.assertEqual(result.owner, "testuser")

    def test_repository_by_clone_url_returns_correct_repository(self):
        clone_url = "https://example.com/repo.git"
        mock_repository = models.Repository(id="repo_123", clone_url=clone_url)
        self.db.query.return_value.filter.return_value.first.return_value = mock_repository

        result = get_repository_by_clone_url(self.db, clone_url)
        self.assertEqual(result.clone_url, clone_url)

    def test_repository_by_id_and_username_returns_owned_repository(self):
        repository_id = "repo_123"
        username = "owner_user"
        mock_repository = models.Repository(id=repository_id, owner=username)
        self.db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_repository

        result = get_repository_by_id_and_username(self.db, repository_id, username)
        self.assertEqual(result.id, repository_id)
        self.assertEqual(result.owner, username)

    def test_repositories_returns_correct_repositories(self):
        mock_repositories = [models.Repository(id=f"repo_{i}") for i in range(3)]
        self.db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_repositories

        result = get_repositories(self.db, skip=0, limit=3)
        self.assertEqual(len(result), 3)

    def test_repositories_by_username_returns_user_repositories(self):
        username = "testuser"
        mock_repositories = [models.Repository(id=f"repo_{i}", owner=username) for i in range(2)]
        self.db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_repositories

        result = get_repositories_by_username(self.db, username, "", skip=0, limit=2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].owner, username)

    def test_repositories_by_username_with_clone_url_filters_correctly(self):
        username = "testuser"
        clone_url = "test-repo"
        mock_repositories = [
            models.Repository(id="repo_1", owner=username, clone_url="https://example.com/test-repo.git")]
        self.db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_repositories

        result = get_repositories_by_username(self.db, username, clone_url, skip=0, limit=10)
        self.assertEqual(len(result), 1)

    def test_shared_repositories_returns_repositories_with_consent(self):
        mock_repositories = [models.Repository(id=f"repo_{i}") for i in range(2)]
        self.db.query.return_value.join.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_repositories

        result = get_shared_repositories(self.db, "", skip=0, limit=2)
        self.assertEqual(len(result), 2)

    def test_shared_repositories_with_clone_url_filters_correctly(self):
        clone_url = "test-repo"
        mock_repositories = [models.Repository(id="repo_1", clone_url="https://example.com/test-repo.git")]
        self.db.query.return_value.join.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_repositories

        result = get_shared_repositories(self.db, clone_url, skip=0, limit=10)
        self.assertEqual(len(result), 1)

    def test_create_repository_saves_repository_correctly(self):
        repo_data = schemas.RepositoryCreate(default_branch="main",
                                             clone_url=HttpUrl("https://example.com/repo.git"))
        username = "testuser"
        mock_repository = models.Repository(**repo_data.dict(), owner=username)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_repository

        result = create_repository(self.db, repo_data, username)
        self.assertEqual(result.owner, username)
        self.assertEqual(str(result.clone_url), str(repo_data.clone_url))

    def test_delete_repository_removes_repository(self):
        repository_id = "repo_123"
        self.db.query.return_value.filter.return_value.delete.return_value = 1

        result = delete_repository(self.db, repository_id)
        self.assertTrue(result)

    # AdditionalData tests
    def test_additional_data_by_repository_returns_correct_data(self):
        repository_id = "repo_123"
        mock_data = models.AdditionalData(id="data_1", repository=repository_id)
        self.db.query.return_value.filter.return_value.first.return_value = mock_data

        result = get_additional_data_by_repository(self.db, repository_id)
        self.assertEqual(result.repository, repository_id)

    def test_additional_data_by_id_returns_correct_data(self):
        data_id = "data_123"
        mock_data = models.AdditionalData(id=data_id)
        self.db.query.return_value.filter.return_value.first.return_value = mock_data

        result = get_additional_data_by_id(self.db, data_id)
        self.assertEqual(result.id, data_id)

    def test_additional_data_returns_all_data(self):
        mock_data_list = [models.AdditionalData(id=f"data_{i}") for i in range(3)]
        self.db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_data_list

        result = get_additional_data(self.db, skip=0, limit=3)
        self.assertEqual(len(result), 3)

    def test_create_additional_data_saves_data_correctly(self):
        repo_id = uuid4()
        data = schemas.AdditionalDataCreate(
            repository=repo_id,
            name="Test Repo",
            language="Python",
            forks_count=10,
            open_issues_count=5
        )
        mock_data = models.AdditionalData(**data.dict())
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_data

        result = create_additional_data(self.db, data)
        self.assertEqual(result.name, "Test Repo")
        self.assertEqual(result.repository, repo_id)

    def test_update_additional_data_updates_fields_correctly(self):
        data_id = "data_123"
        repo_id = uuid4()
        updated_data = schemas.AdditionalDataUpdate(
            repository=repo_id,
            name="Updated Repo",
            full_name="Updated Full Name",
            language="JavaScript",
            forks_count=20,
            open_issues_count=10,
            created_at=datetime.now(),
            pushed_at=datetime.now()
        )
        mock_data = models.AdditionalData(id=data_id)
        self.db.query.return_value.filter.return_value.first.return_value = mock_data

        result = update_additional_data(self.db, data_id, updated_data)
        self.assertEqual(result.name, "Updated Repo")
        self.assertEqual(result.language, "JavaScript")
        self.assertEqual(result.forks_count, 20)

    def test_delete_additional_data_removes_data(self):
        data_id = "data_123"
        self.db.query.return_value.filter.return_value.delete.return_value = 1

        result = delete_additional_data(self.db, data_id)
        self.assertTrue(result)

    # Pipeline tests
    def test_pipeline_by_id_returns_correct_pipeline(self):
        pipeline_id = "pipeline_123"
        mock_pipeline = models.Pipeline(id=pipeline_id)
        self.db.query.return_value.filter.return_value.first.return_value = mock_pipeline

        result = get_pipeline_by_id(self.db, pipeline_id)
        self.assertEqual(result.id, pipeline_id)

    def test_pipelines_returns_all_pipelines(self):
        mock_pipelines = [models.Pipeline(id=f"pipeline_{i}") for i in range(3)]
        self.db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_pipelines

        result = get_pipelines(self.db, skip=0, limit=3)
        self.assertEqual(len(result), 3)

    def test_pipelines_by_repository_returns_repository_pipelines(self):
        repository_id = "repo_123"
        mock_pipelines = [models.Pipeline(id=f"pipeline_{i}", repository=repository_id) for i in range(2)]
        self.db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_pipelines

        result = get_pipelines_by_repository(self.db, repository_id, skip=0, limit=2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].repository, repository_id)

    def test_create_pipeline_saves_pipeline_correctly(self):
        repo_id = uuid4()
        pipeline_data = schemas.PipelineCreate(
            repository=repo_id,
            stage=StageEnum.CLONE,
            status=StatusEnum.IN_PROGRESS
        )
        mock_pipeline = models.Pipeline(**pipeline_data.dict())
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_pipeline

        result = create_pipeline(self.db, pipeline_data)
        self.assertEqual(result.repository, repo_id)
        self.assertEqual(result.stage, StageEnum.CLONE)
        self.assertEqual(result.status, StatusEnum.IN_PROGRESS)

    def test_share_consent_pipeline_updates_share_consent_flag(self):
        pipeline_id = "pipeline_123"
        mock_pipeline = models.Pipeline(id=pipeline_id, share_consent=False)
        self.db.query.return_value.filter.return_value.first.return_value = mock_pipeline

        result = share_consent_pipeline(self.db, pipeline_id, share_consent=True)
        self.assertTrue(result.share_consent)

    def test_delete_pipeline_removes_pipeline(self):
        pipeline_id = "pipeline_123"
        self.db.query.return_value.filter.return_value.delete.return_value = 1

        result = delete_pipeline(self.db, pipeline_id)
        self.assertTrue(result)

    # User tests
    def test_user_by_id_returns_correct_user(self):
        user_id = "user_123"
        mock_user = models.User(id=user_id, username="testuser")
        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        result = get_user_by_id(self.db, user_id)
        self.assertEqual(result.id, user_id)
        self.assertEqual(result.username, "testuser")

    def test_user_by_username_active_returns_active_user(self):
        username = "active_user"
        mock_user = models.User(username=username, status=UserStatusEnum.ACTIVE)
        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        result = get_user_by_username_active(self.db, username)
        self.assertEqual(result.username, username)
        self.assertEqual(result.status, UserStatusEnum.ACTIVE)

    def test_user_exists_returns_true_when_user_exists(self):
        username = "existing_user"
        self.db.query.return_value.filter.return_value.first.return_value = models.User(username=username)

        result = user_exists(self.db, username)
        self.assertTrue(result)

    def test_user_exists_returns_false_when_user_does_not_exist(self):
        username = "nonexistent_user"
        self.db.query.return_value.filter.return_value.first.return_value = None

        result = user_exists(self.db, username)
        self.assertFalse(result)

    def test_create_user_saves_user_correctly(self):
        user_data = schemas.UserCreate(
            username="testuser",
            password="password123",
            confirm_password="password123",
            fullname="Test User",
            email="test@example.com"
        )
        mock_user = models.User(
            id=uuid4(),
            username="testuser",
            hashed_password="hashed_password",
            fullname="Test User",
            email="test@example.com",
            status=UserStatusEnum.ACTIVE,
            created_at=datetime.now()
        )
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_user

        result = create_user(self.db, user_data)
        self.assertEqual(result.username, user_data.username)
        self.assertEqual(result.fullname, user_data.fullname)
        self.assertEqual(result.status, UserStatusEnum.ACTIVE)

    def test_save_integration_user_creates_new_user_when_not_exists(self):
        username = "github_user"
        github_token = "test_token"
        self.db.query.return_value.filter.return_value.first.return_value = None
        mock_user = models.User(
            id=uuid4(),
            username=username,
            github_token=github_token,
            github_user=True,
            status=UserStatusEnum.ACTIVE
        )
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_user

        result = save_integration_user(self.db, username, github_token)
        self.assertEqual(result.username, username)
        self.assertEqual(result.github_token, github_token)
        self.assertTrue(result.github_user)

    def test_save_integration_user_updates_existing_user(self):
        username = "github_user"
        github_token = "test_token"
        existing_user = models.User(
            id=uuid4(),
            username=username,
            github_user=True,
            github_token="old_token"
        )
        self.db.query.return_value.filter.return_value.first.return_value = existing_user
        self.db.commit.return_value = None
        self.db.refresh.return_value = existing_user

        result = save_integration_user(self.db, username, github_token)
        self.assertEqual(result.github_token, github_token)

    def test_get_user_by_token_active_returns_correct_user(self):
        token = "test_token"
        mock_user = models.User(id=uuid4(), username="testuser", github_token=token)
        self.db.query.return_value.filter.return_value.first.return_value = mock_user

        result = get_user_by_token_active(self.db, token)
        self.assertEqual(result.github_token, token)

    def test_get_user_by_token_active_returns_none_for_invalid_token(self):
        token = "invalid_token"
        self.db.query.return_value.filter.return_value.first.return_value = None

        result = get_user_by_token_active(self.db, token)
        self.assertIsNone(result)

    def test_create_commit_saves_commit_correctly(self):
        commit_data = {
            "id": uuid4(),
            "pipeline_id": uuid4(),
            "author_name": "Test Author",
            "committer_name": "Test Committer",
            "author_date": "2020-01-01T00:00:00Z",
            "message": "Test commit"
        }
        mock_commit = models.Commit(**commit_data)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_commit

        result = create_commit(self.db, commit_data)
        self.assertEqual(result.author_name, "Test Author")
        self.assertEqual(result.committer_name, "Test Committer")
        self.assertEqual(result.message, "Test commit")
        self.assertEqual(result.author_date, "2020-01-01T00:00:00Z")

    def test_create_test_data_saves_test_data_correctly(self):
        test_data = {
            "id": uuid4(),
            "pipeline_id": uuid4(),
            "file_path": "src/module/test_file.py",
            "is_test_file": True,
            "has_test_import": True,
            "has_test_call": True,
            "commit_order": 1
        }
        mock_test_data = models.TestData(**test_data)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_test_data

        result = create_test_data(self.db, test_data)
        self.assertEqual(result.commit_order, 1)
        self.assertEqual(result.file_path, "src/module/test_file.py")
        self.assertTrue(result.is_test_file)
        self.assertTrue(result.has_test_import)
        self.assertTrue(result.has_test_call)

    def test_get_test_datas_by_pipeline_returns_ordered_data(self):
        pipeline_id = uuid4()
        mock_test_datas = [
            models.TestData(id=1, commit_order=2),
            models.TestData(id=2, commit_order=1)
        ]
        self.db.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_test_datas

        result = get_tests_data_by_pipeline(self.db, pipeline_id)
        self.assertEqual(len(result), 2)

    def test_create_code_metrics_saves_metrics_correctly(self):
        code_metrics = {
            "id": uuid4(),
            "pipeline_id": uuid4(),
            "full_name": "test",
            "timeseries": [0, 100, 200, 300, 400, 500, 800, 1000],
            "metric_type": "production"
        }
        mock_metrics = models.CodeMetrics(**code_metrics)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_metrics

        result = create_code_metrics(self.db, code_metrics)
        self.assertEqual(result.full_name, "test")
        self.assertEqual(result.timeseries, [0, 100, 200, 300, 400, 500, 800, 1000])
        self.assertEqual(result.metric_type, "production")

    def test_create_project_dimension_saves_dimension_correctly(self):
        project_dimension = {
            "id": uuid4(),
            "pipeline_id": uuid4(),
            "n_commits": 3,
            "n_devs": 4,
            "n_forks_count": 5,
            "n_open_issues_count": 6,
        }

        mock_dimension = models.ProjectDimension(**project_dimension)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_dimension

        result = create_project_dimension(self.db, project_dimension)
        self.assertEqual(result.n_commits, 3)
        self.assertEqual(result.n_devs, 4)
        self.assertEqual(result.n_forks_count, 5)
        self.assertEqual(result.n_open_issues_count, 6)

    def test_create_commit_message_item_saves_item_correctly(self):
        commit_message_item = {
            "id": uuid4(),
            "pipeline_id": uuid4(),
            "hash": "abc123def456",
            "message": "feat: add new feature",
            "bug_fix_regex_count": 0,
            "adaptive_regex_count": 0,
            "adaptive_by_negation_regex_count": 0,
            "perfective_regex_count": 2,
            "refactor_regex_count": 0,
            "is_perfective": True,
            "is_refactor": False,
            "is_adaptive": False,
            "is_adaptive_by_negation": False,
            "is_corrective": False,
            "perfective_in_text": {"matches": ["improve", "enhance"]},
            "refactor_in_text": None,
            "adaptive_in_text": None,
            "adaptive_by_negation_in_text": None,
            "corrective_in_text": None,

        }
        mock_item = models.CommitMessageItem(**commit_message_item)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_item

        result = create_commit_message_item(self.db, commit_message_item)
        self.assertEqual(result.hash, "abc123def456")
        self.assertEqual(result.message, "feat: add new feature")
        self.assertEqual(result.perfective_regex_count, 2)
        self.assertTrue(result.is_perfective)
        self.assertFalse(result.is_refactor)
        self.assertFalse(result.is_adaptive)
        self.assertFalse(result.is_adaptive_by_negation)
        self.assertFalse(result.is_corrective)
        self.assertEqual(result.perfective_in_text, {"matches": ["improve", "enhance"]})
        self.assertIsNone(result.refactor_in_text)
        self.assertIsNone(result.adaptive_in_text)
        self.assertIsNone(result.adaptive_by_negation_in_text)
        self.assertIsNone(result.corrective_in_text)

    def test_create_maintenance_activity_summary_saves_summary_correctly(self):
        maintenance_summary = {
            "id": uuid4(),
            "pipeline_id": uuid4(),
            "n_corrective": 20.5,
            "n_perfective": 40.2,
            "n_adaptive": 29.3,
            "n_multi": 10
        }
        mock_summary = models.MaintenanceActivitySummary(**maintenance_summary)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_summary

        result = create_maintenance_activity_summary(self.db, maintenance_summary)
        self.assertEqual(result.n_corrective, 20.5)
        self.assertEqual(result.n_perfective, 40.2)
        self.assertEqual(result.n_adaptive, 29.3)
        self.assertEqual(result.n_multi, 10)

    def test_create_correlation_saves_correlation_correctly(self):
        correlation_data = {
            "id": uuid4(),
            "pipeline_id": uuid4(),
            "pearson_correlation": 0.85
        }
        mock_correlation = models.Correlation(**correlation_data)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_correlation

        result = create_correlation(self.db, correlation_data)
        self.assertEqual(result.pearson_correlation, 0.85)

    def test_create_code_detail_saves_detail_correctly(self):
        detail_data = {
            "id": uuid4(),
            "pipeline_id": uuid4(),
            "commit_order": 1,
            "path": "src/main.py",
            "loc": 150
        }
        mock_detail = models.CodeDistributionDetail(**detail_data)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_detail

        result = create_code_distribution_details(self.db, detail_data)
        self.assertEqual(result.commit_order, 1)
        self.assertEqual(result.path, "src/main.py")
        self.assertEqual(result.loc, 150)

    def test_create_insights_saves_insights_correctly(self):
        insights_data = {
            "id": uuid4(),
            "pipeline_id": uuid4(),
            "generated_text": "value_insight"
        }
        mock_insights = models.Insights(**insights_data)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = mock_insights

        result = create_insights(self.db, insights_data)
        self.assertEqual(result.generated_text, "value_insight")


if __name__ == "__main__":
    unittest.main()