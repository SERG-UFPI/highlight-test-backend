import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import sessionmaker
from app.database import get_db, engine, SessionLocal

class TestDatabase(unittest.TestCase):

    @patch("app.database.SessionLocal")
    def test_get_db(self, mock_session_local):
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        # Simulate the generator behavior of get_db
        db_generator = get_db()
        db = next(db_generator)
        self.assertEqual(db, mock_session)

        # Ensure the session is closed after use
        with self.assertRaises(StopIteration):
            next(db_generator)
        mock_session.close.assert_called_once()

    def test_session_local_configuration(self):
        self.assertIsInstance(SessionLocal, sessionmaker)
        self.assertEqual(SessionLocal.kw["autocommit"], False)
        self.assertEqual(SessionLocal.kw["autoflush"], False)
        self.assertEqual(SessionLocal.kw["bind"], engine)

if __name__ == "__main__":
    unittest.main()