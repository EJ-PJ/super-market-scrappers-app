from app.clients.super_fresh_client import SuperFreshClient
from app.parser.super_fresh_product_parser import SuperFreshScrapperProduct
import json

class SuperFreshScrapper:

    # Constructor
    def __init__(self):
        
        self.product_super_fresh = None
        self.parse_super_fresh_produtcs = None

    def search_products(self, product):
        super_fresh_client = SuperFreshClient()

        # Search for products
        self.product_super_fresh = super_fresh_client.search_products(product)

        print("type super_fresh_: ", type(self.product_super_fresh).__name__)

        # Parse praducts for show in new json
        super_fresh_p_p = SuperFreshScrapperProduct()
        parse_products = super_fresh_p_p.product_parser(products=self.product_super_fresh)

        print("sp_products: ", parse_products)
        
        self.parse_super_fresh_produtcs = parse_products

        return self.parse_super_fresh_produtcs
