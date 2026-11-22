from app.clients.maxi_despensa_client import MaxiDespensaClient
from app.parser.maxi_despensa_product_parser import MaxiDespensaScrapperProduct


class MaxiDespensaScrapper:

    def search_products(self, product: str, page: int, page_size: int, postal_code: str | None = None) -> list[dict]:
        # VTEX uses from / to indexes and "to" is inclusive (from=0, to=19 -> 20 products)
        from_index = (page - 1) * page_size
        to_index = from_index + page_size - 1

        raw_products = MaxiDespensaClient().search_products(product, from_index, to_index, postal_code)

        return MaxiDespensaScrapperProduct().product_parser(raw_products)
