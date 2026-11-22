from app.clients.super_fresh_client import SuperFreshClient
from app.parser.super_fresh_product_parser import SuperFreshScrapperProduct


class SuperFreshScrapper:

    # with postal_code the client uses the closest Super Fresh store to that zone
    def search_products(self, product: str, page: int, page_size: int, postal_code: str | None = None) -> list[dict]:
        raw_products = SuperFreshClient().search_products(product, postal_code)

        parsed = SuperFreshScrapperProduct().product_parser(raw_products)

        # the Super Fresh API returns every result at once, so paginate here
        start = (page - 1) * page_size
        return parsed[start:start + page_size]
