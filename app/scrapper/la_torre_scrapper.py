from app.clients.la_torre_client import LaTorreClient
from app.parser.la_torre_product_parser import LaTorreScrapperProduct


class LaTorreScrapper:

    def search_products(self, product: str, page: int, page_size: int, postal_code: str | None = None) -> list[dict]:
        # VTEX uses from / to indexes and "to" is inclusive (from=0, to=19 -> 20 products)
        from_index = (page - 1) * page_size
        to_index = from_index + page_size - 1

        raw_products = LaTorreClient().search_products(product, from_index, to_index, postal_code)

        return LaTorreScrapperProduct().product_parser(raw_products)
