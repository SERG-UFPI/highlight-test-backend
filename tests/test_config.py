import unittest
from unittest.mock import patch
from app.config import *

class TestConfig(unittest.TestCase):

    @patch.dict(os.environ, {
        "SERVER_BASE_URL": "http://localhost:8000",
        "AUTH_SECRET_KEY": "test_secret_key",
        "AUTH_ALGORITHM": "HS256",
        "AUTH_ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "SQLALCHEMY_DATABASE_URL": "sqlite:///./test.db",
        "CELERY_BROKER_URL": "redis://localhost:6379/0",
        "CELERY_BACKEND": "redis://localhost:6379/0",
        "GITHUB_CLIENT_ID": "test_client_id",
        "GITHUB_CLIENT_SECRET": "test_client_secret",
        "GITHUB_REDIRECT_URI": "http://localhost:8000/callback",
        "GITHUB_REDIRECT_FRONTEND": "http://localhost:3000",
        "GEMINI_API_KEY": "test_gemini_api_key",
        "FRONTEND_URL": "http://localhost:3000",
        "SERVER_HOST": "127.0.0.1",
        "SERVER_PORT": "8000",
        "SERVER_RESULTS_PATH": "/var/results",

    })
    def test_environment_variables(self):
        self.assertIsNotNone(SERVER_BASE_URL)
        self.assertIsNotNone(AUTH_SECRET_KEY)
        self.assertIsNotNone(AUTH_ALGORITHM)
        self.assertIsNotNone(AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
        self.assertIsNotNone(SQLALCHEMY_DATABASE_URL)
        self.assertIsNotNone(CELERY_BROKER_URL)
        self.assertIsNotNone(CELERY_BACKEND)
        self.assertIsNotNone(GITHUB_CLIENT_ID)
        self.assertIsNotNone(GITHUB_CLIENT_SECRET)
        self.assertIsNotNone(GITHUB_REDIRECT_URI)
        self.assertIsNotNone(GITHUB_REDIRECT_FRONTEND)
        self.assertIsNotNone(GEMINI_API_KEY)
        self.assertIsNotNone(FRONTEND_URL)
        self.assertIsNotNone(SERVER_HOST)
        self.assertIsNotNone(SERVER_PORT)
        self.assertIsNotNone(SERVER_RESULTS_PATH)

if __name__ == "__main__":
    unittest.main()