from clients import SuperFreshClient


class SuperFreshScrapper(SuperFreshClient):

    # Constructor
    def __init__(self):
        self.product_superfresh

    def search_products(self, product):
        self.product_superfresh = self.search_products()
        return self.product_superfresh
