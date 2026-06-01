import unittest
from app import app

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data.decode(),
            "Welcome to Flask Testing"
        )

    def test_add_route(self):
        response = self.app.get('/add/10/20')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "30")

if __name__ == "__main__":
    unittest.main()