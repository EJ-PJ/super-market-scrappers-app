from app.clients.super_fresh_client import SuperFreshClient


class SuperFreshScrapper:

    # Constructor
    def __init__(self):
        
        self.product_super_fresh = None

    def search_products(self, product):
        super_fresh_client = SuperFreshClient()

        self.product_super_fresh = super_fresh_client.search_products(product)
        print("type: ", type(self.product_super_fresh).__name__)

        return self.product_super_fresh
