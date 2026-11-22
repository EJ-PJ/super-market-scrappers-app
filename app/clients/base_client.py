import requests

# HTTP handler whit GET and POST methods

# seconds to wait for a supermarket before giving up
DEFAULT_TIMEOUT = 15


class BaseClient:

    def __init__(self):
        self.session = requests.Session()

    def get(self, url, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        response = self.session.get(url, **kwargs)

        response.raise_for_status()

        return response

    def post(self, url, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        response = self.session.post(url, **kwargs)

        response.raise_for_status()

        return response
