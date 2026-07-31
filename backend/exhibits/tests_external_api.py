import json
from unittest.mock import patch

from django.test import TestCase


class _MockResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode('utf-8')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class ExternalApiProxyTests(TestCase):
    @patch('exhibits.views.urlopen')
    def test_exchange_rates_proxy_returns_rates(self, mock_urlopen):
        mock_urlopen.return_value = _MockResponse(
            {
                'amount': 1,
                'base': 'USD',
                'date': '2026-07-31',
                'rates': {'EUR': 0.92, 'GBP': 0.78},
            }
        )

        response = self.client.get('/api/external/exchange-rates/?base=USD&symbols=EUR,GBP')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['provider'], 'frankfurter')
        self.assertIn('EUR', response.json()['rates'])

    @patch('exhibits.views.urlopen')
    def test_museum_search_proxy_returns_curated_results(self, mock_urlopen):
        def fake_urlopen(request, timeout=6):
            url = request.full_url
            if '/search?' in url:
                return _MockResponse({'total': 1, 'objectIDs': [123]})
            if '/objects/123' in url:
                return _MockResponse(
                    {
                        'objectID': 123,
                        'title': 'Water Lilies',
                        'artistDisplayName': 'Claude Monet',
                        'objectDate': '1916',
                        'primaryImageSmall': 'https://images.example/123.jpg',
                        'objectURL': 'https://www.metmuseum.org/art/collection/search/123',
                        'repository': 'The Metropolitan Museum of Art',
                    }
                )
            return _MockResponse({})

        mock_urlopen.side_effect = fake_urlopen

        response = self.client.get('/api/external/museum-search/?q=monet')

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['provider'], 'the-met')
        self.assertEqual(len(body['results']), 1)
        self.assertEqual(body['results'][0]['title'], 'Water Lilies')

    def test_museum_search_requires_query(self):
        response = self.client.get('/api/external/museum-search/')

        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.json())
