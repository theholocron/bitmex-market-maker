import os
import logging
import requests
from django.conf import settings
from bitmex.auth import BitmexAPIAuth


class Bitmex(object):

    RATE_LIMIT_PER_MINUTE = os.getenv('RATE_LIMIT_PER_MINUTE', 60)

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _make_request(self, method, endpoint, params):
        """send a https request and returns the response for a generic api call"""
        url = os.path.join(settings.BITMEX_BASE_URL, endpoint)
        self.logger.debug(f'Initiaing http request for API {endpoint} with params {params}')
        return requests.request(method=method, url=url, json=params, auth=BitmexAPIAuth())

    @property
    def position(self):
        """api call to return open positions in the current account"""
        response = self._make_request('GET', 'position', {})
        diagnosis = self._diagnose_api_resp(response)
        return diagnosis['json']

    def _diagnose_api_resp(self, response):
        diagnosis = {
            'status_code': response.status_code,
            'json': response.json(),
            'x-ratelimit-limit': response.headers['x-ratelimit-limit'],
            'x-ratelimit-remaining': response.headers['x-ratelimit-remaining'],
            'x-ratelimit-reset': response.headers['x-ratelimit-reset']
        }
        self.logger.debug(f'API response: {diagnosis}')
        return diagnosis
