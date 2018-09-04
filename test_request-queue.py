import unittest
from RequestQueue import RequestQueue
import requests


class RequestQueueTestCase(unittest.TestCase):

    def test_success(self):
        q = RequestQueue(num_workers=1)
        url = 'https://openlibrary.org/api/books?bibkeys=ISBN:0451526538&format=json'
        for item in range(10):
            q.send_request(url=url)

        q.join()
        results = q.get_results()
        self.assertIsNotNone(results)

        for result in results:
            self.assertIsNotNone(result)
            self.assertEqual(result.status_code, 200)

    def test_connectionError(self):
        q = RequestQueue(num_workers=1)
        url = 'https://wrong_url.org/api/books?bibkeys=ISBN:0451526538&format=json'
        for item in range(10):
            q.send_request(url=url)

        q.join()
        results = q.get_results()
        self.assertIsNotNone(results)

        for result in results:
            self.assertIsNotNone(result)
            self.assertTrue(isinstance(result, requests.exceptions.ConnectionError))

    

if __name__ == '__main__':
    unittest.main()
