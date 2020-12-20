import unittest
from immoweb_scraper import handler
from moto import mock_s3

class MyTestCase(unittest.TestCase):

    @mock_s3
    def test_scraper_with_no_errors(self):
        handler(None, None)


if __name__ == '__main__':
    unittest.main()
