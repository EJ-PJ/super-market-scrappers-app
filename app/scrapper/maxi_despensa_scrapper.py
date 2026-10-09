from app.clients.maxi_despensa_client import MaxiDespensaClient
from app.parser.maxi_despensa_product_parser import MaxiDespensaScrapperProduct

class MaxiDespensaScrapper:

    # Constructor
    def __init__(self):
        
        self.product_maxi_despensa = None
        self.parse_products_maxi_despensa = None

    def search_products(self, product,  from_page, to_page):
        maxi_despensa_client = MaxiDespensaClient() 

        # Search products
        self.product_maxi_despensa = maxi_despensa_client.search_products(product, from_page, to_page)

        print("type maxi_despensa ", type(self.product_maxi_despensa).__name__)        

        # Parser products
        maxi_despensa_p_p = MaxiDespensaScrapperProduct()
        self.parse_products_maxi_despensa = maxi_despensa_p_p.product_parser(self.product_maxi_despensa)

        print("parse products: ", self.parse_products_maxi_despensa)

        return self.parse_products_maxi_despensa
