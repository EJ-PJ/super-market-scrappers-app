from app.clients.paiz_client import PaizClient
from app.parser.paiz_product_parser import PaizScrapperProduct


class PaizScrapper:

    def search_products(self, product: str, page: int, page_size: int, postal_code: str | None = None) -> list[dict]:
        # VTEX uses from / to indexes and "to" is inclusive (from=0, to=19 -> 20 products)
        from_index = (page - 1) * page_size
        to_index = from_index + page_size - 1

        raw_products = PaizClient().search_products(product, from_index, to_index, postal_code)

        return PaizScrapperProduct().product_parser(raw_products)

    def get_branch(self, postal_code: str | None = None) -> dict | None:
        # name / address of the store used for this postal code
        return PaizClient().get_branch(postal_code)
