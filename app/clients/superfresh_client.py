from . import BaseClient


class SuperFreshClient(BaseClient):

    # https://msf-api.gta.com.gt/api/products/search
    base_url = "https://msf-api.gta.com.gt/api/products/search"

    def search_products(self, query):
        response = self.post(
            self.base_url,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
                 'Accept: */*',
                 "Accept-Encoding: gzip, deflate, br, zstd',
                 'Accept-Language: en-US,en;q=0.9',
                 'Connection: keep-alive',
                 'Content-Type: application/json',
                 'Origin: https://www.misuperfresh.com.gt',
                 'Referer: https://www.misuperfresh.com.gt/',
                 'Sec-Fetch-Dest: empty',
                 'Sec-Fetch-Mode: cors',
                 'Sec-Fetch-Site: cross-site',
                 'TE: trailers',
                 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0'
            },
            json={
                "query": query
            },
            timeout=10
        )

        return response.json()


