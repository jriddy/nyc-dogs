import unittest
import requests
import os


class TestDogAPI(unittest.TestCase):

    def setUp(self):
        self.base_url = os.environ["READY_TEST_BASE_URL"]

    def base(self, path):
        return self.base_url + path

    def test_unknown(self):
        rawresp = requests.get(self.base("/count"),
                params={'foo': 'x', 'bar': 'y', 'baz': 'z'})
        self.assertEqual(rawresp.status_code, 400)
        resp = rawresp.json()
        self.assertEqual(resp['unknown fields'], ['bar', 'baz', 'foo'])

    def test_content_type(self):
        rawresp = requests.get(self.base("/count"), params={'dog_name': 'Buddy'})
        self.assertEqual(rawresp.headers['Content-Type'], 'application/json')

    def test_count_one(self):
        rawresp = requests.get(self.base("/count"), params={'dog_name': 'Buddy'})
        resp = rawresp.json()
        self.assertEqual(resp['count'], 599)

    def test_count_two(self):
        rawresp = requests.get(self.base("/count"),
                params={'gender': 'f', 'dominant_color': 'brindle'})
        resp = rawresp.json()
        self.assertEqual(resp['count'], 1245)

    def test_count_three(self):
        rawresp = requests.get(self.base("/count"), params={
            'gender': 'm',
            'borough': 'brooklyn',
            'spayed_or_neutered': 'no'})
        resp = rawresp.json()
        self.assertEqual(resp['count'], 3230)


if __name__ == '__main__':
    unittest.main()