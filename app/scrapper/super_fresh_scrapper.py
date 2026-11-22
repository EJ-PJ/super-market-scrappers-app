from app.clients.super_fresh_client import SuperFreshClient
from app.parser.super_fresh_product_parser import SuperFreshScrapperProduct


class SuperFreshScrapper:

    # postal_code is ignored for now: Super Fresh picks the store with its own
    # store code ({"store": {"code": 2}} in the client)
    def search_products(self, product: str, page: int, page_size: int, postal_code: str | None = None) -> list[dict]:
        raw_products = SuperFreshClient().search_products(product)

        parsed = SuperFreshScrapperProduct().product_parser(raw_products)

        # the Super Fresh API returns every result at once, so paginate here
        start = (page - 1) * page_size
        return parsed[start:start + page_size]
