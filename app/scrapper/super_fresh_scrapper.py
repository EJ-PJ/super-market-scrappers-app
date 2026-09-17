from app.clients import SuperFreshClient


class SuperFreshScrapper(SuperFreshClient):

    # Constructor
    def __init__(self):
        super().__init__()
        self.product_superfresh = None

    def search_products(self, product):
        self.product_superfresh = super().search_products(product)
        return self.product_superfresh
