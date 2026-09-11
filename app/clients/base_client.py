import requests


class BaseClient:

    def __init__(self):
        self.session = requests.Session()

    def get(self, url, **kwargs):
        response = self.session.get(url, **kwargs)

        response.raise_for_status()

        return response

    def post(self, url, **kwargs):
        response = self.session.post(url, **kwargs)

        response.raise_for_status()

        return response
