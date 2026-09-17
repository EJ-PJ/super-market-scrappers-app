from app.scrapper import SuperFreshScrapper


class Products(SuperFreshScrapper):

    def __init__(self):
        super().__init__()
        self.products_superfresh = None

    def search_products(self, product):
        self.products_superfresh = super().search_products(product)
        return self.products_superfresh
