from app.scrapper.super_fresh_scrapper import SuperFreshScrapper
from app.scrapper.maxi_despensa_scrapper import MaxiDespensaScrapper

class Products:

    def __init__(self):
        self.products_ = None

    def search_products(self, product):

        super_fresh_scrapper = SuperFreshScrapper()

        maxi_despensa_scrapper = MaxiDespensaScrapper()

        self.products_ = super_fresh_scrapper.search_products(product)

        return self.products_

    def search_products_maxi_despensa(self, product, from_, to_):
        maxi_despensa_scrapper = MaxiDespensaScrapper()

        self.products_ = maxi_despensa_scrapper.search_products(product, from_, to_)

        return self.products_

    def search_products_super_fresh(self, product):

        super_fresh_scrapper = SuperFreshScrapper()

        self.products_ = super_fresh_scrapper.search_products(product)

        return self.products_
