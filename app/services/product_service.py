from app.scrapper import SuperFreshScrapper


class Products(SuperFreshScrapper):

    def __init__(self):
        super().__init__()
        self.products_super_fresh = None

    def search_products(self, product):
        self.products_super_fresh = super().search_products(product)
        return self.products_super_fresh
