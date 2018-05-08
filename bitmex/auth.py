import hmac
import hashlib
import requests
import settings
from time import time


class BitmexAPIAuth(requests.auth.AuthBase):

    def __call__(self, request):
        """called at the time of forming http request - generates http headers for auth"""
        request.headers['Accept'] = "application/json"
        request.headers['api-nonce'] = self.generate_nonce()
        request.headers['api-key'] = settings.BITMEX_API_KEY
        request.headers['api-signature'] = self.generate_signature(request)
        return request

    def generate_nonce(self):
        return int(round(time())) * 1000

    def generate_signature(self, request):
        parsed_url = requests.urllib3.util.parse_url(request.url)
        path = parsed_url.path
        if parsed_url.query:
            path = path + '?' + parsed_url.query

        data = request.body
        if isinstance(data, (bytes, bytearray)):
            data = data.decode('utf8')

        message = request.method + path + str(request.headers['api-nonce']) + (data or '')
        api_secret = settings.BITMEX_API_SECRET
        return hmac.new(bytes(api_secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
