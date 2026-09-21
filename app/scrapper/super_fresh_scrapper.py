from app.clients.super_fresh_client import SuperFreshClient


class SuperFreshScrapper(SuperFreshClient):

    # Constructor
    def __init__(self):
        super().__init__()
        self.product_super_fresh = None

    def search_products(self, product):
        self.product_super_fresh = super().search_products(product)
        return self.product_super_fresh
