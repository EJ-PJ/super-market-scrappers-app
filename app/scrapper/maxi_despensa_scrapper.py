from app.clients.maxi_despensa_client import MaxiDespensaClient


class MaxiDespensaScrapper:

    # Constructor
    def __init__(self):
        
        self.product_maxi_despensa = None

    def search_products(self, product,  from_page, to_page):
        maxi_despensa_client = MaxiDespensaClient() 

        self.product_maxi_despensa = maxi_despensa_client.search_products(product, from_page, to_page)

        #print("product scrapper: ", self.product_maxi_despensa)

        return self.product_maxi_despensa
