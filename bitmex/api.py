import os
import time
import logging
import requests
from django.conf import settings
from bitmex.auth import BitmexAPIAuth
from bitmex.errors import (
    MarketOverloadError,
    RetryLimitExceededError,
    APIParameterError,
    UnauthorizedError
)


logger = logging.getLogger(__name__)


class BitmexAPIConnector(object):
    """
    API documentation has been described here
        - https://www.bitmex.com/api/explorer/

    Handling Auth for API has been described here
        - https://www.bitmex.com/app/apiKeysUsage
    """

    RATE_LIMIT_PER_MINUTE = os.getenv('RATE_LIMIT_PER_MINUTE', 60)

    ##############################################################
    ######## INTERNAL / PRIVATE FUNCTIONS AND VARIABLES ##########
    ##############################################################

    @property
    def RATELIMIT_REMAINING(self):
        """number of api calls remaining before next reset occurs"""
        return self._ratelimit_remaining

    @property
    def RATELIMIT_RESET(self):
        """time in seconds to reset api rate limits"""
        return self._ratelimit_reset

    def __init__(self):
        self._ratelimit_remaining = -1
        self._ratelimit_reset = -1
        self.locked = False
        self.timestamp = int(time.time())

    def _make_request(self, method, endpoint, params={}):
        """
        send a https request and returns the response for a generic api call
        the `locked` field on an instance will allow once instance of this
        class to make only one call to the api

        TODO: can we enforce that this function will remain `internal`?
        """

        if self.locked:
            return {}

        url = os.path.join(settings.BITMEX_BASE_URL, endpoint)
        logger.debug(f'Initiaing http request for API {endpoint} with params {params}')
        response = requests.request(method=method, url=url, json=params, auth=BitmexAPIAuth())
        diagnosis = self._diagnose_api_resp(response)
        self.locked = True
        return response.json()

    def _diagnose_api_resp(self, response):
        """as described at https://www.bitmex.com/app/restAPI and https://www.bitmex.com/api/explorer/"""

        self._ratelimit_remaining = response.headers['x-ratelimit-remaining']
        self._ratelimit_reset = response.headers['x-ratelimit-reset']

        if response.status_code == 503:
            raise MarketOverloadError(response.json()['error']['message'])
        elif response.status_code == 429:
            raise RetryLimitExceededError(f"Resets in {self.RATELIMIT_RESET} seconds")
        elif response.status_code == 400:
            raise APIParameterError(response.json()['error']['message'])
        elif response.status_code == 400:
            raise UnauthorizedError(response.json()['error']['message'])
