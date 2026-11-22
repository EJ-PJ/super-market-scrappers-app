from .base_client import BaseClient


class SuperFreshClient:

    # https://msf-api.gta.com.gt/api/products/search
    base_url = "https://msf-api.gta.com.gt/api/products/search"

    body =  {
             "version": "5.1.6",
             "channel": "web",
             "search_term": "Monster",
             "qty": 0,
             "store": {"code": 2}
             }

    def search_products(self, product):
        # copy so the class-level body is never mutated between requests
        body = {**self.body, "search_term": product}

        base_client = BaseClient()

        response = base_client.post(
            self.base_url,
            json=body,
            headers={
                'Accept': "*/*",
                'Accept-Encoding': "gzip, deflate, br, zstd",
                'Accept-Language': "en-US,en;q=0.9",
                'Connection': "keep-alive",
                'Content-Type': "application/json",
                'Origin': "https://www.misuperfresh.com.gt",
                'Referer': "https://www.misuperfresh.com.gt/",
                'Sec-Fetch-Dest': "empty",
                'Sec-Fetch-Mode': "cors",
                'Sec-Fetch-Site': "cross-site",
                'TE': "trailers",
                'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0"
            },
        )

        return response.json()
