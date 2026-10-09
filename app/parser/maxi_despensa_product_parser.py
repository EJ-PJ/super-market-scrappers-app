from app.parser.promo_parser_maxi_despensa import ParserPromo


class MaxiDespensaScrapperProduct:

    def product_parser(self, products : dict):
        md_products = {
                    "maxi_despensa" : {
                    "products" : []
                    }
                }

        print()
        print()
        print()
        print()
        print()
        
        #print("p_p: ", products['data']['productSearch']['products'][0])

        parser_promo = ParserPromo()

        i = 0
        for product in products['data']['productSearch']['products']:
            product_desp = {
                    "description" : "",
                    # ListPrice means the Real Price
                    "ListPrice" : "",
                    # Price is the price whit disccount
                    "Price": "",
                    "img" : "",
                    "offerHighlight": [],
                    "url" : ""
			} 
            print(i, ".", product['productName'])
            # setting product name
            product_desp['description'] = product.get('productName')
            # setting product ListPrice
            product_desp['ListPrice'] = self.safe_get(product, "items", 0, "sellers", 0, "commertialOffer", "ListPrice")
            # setting prodcut Price
            product_desp['Price'] = self.safe_get(product, "items", 0, "sellers", 0, "commertialOffer", "Price")
            # setting offerHighlight
            product_desp['offerHighlight'].append(parser_promo.extract_promos(product))
            # setting img 
            product_desp['img'] = self.safe_get(product, "items", 0, "images", 0, "imageUrl")
            # Url
            link = product.get('linkText')
            url = f"https://www.maxidespensa.com.gt/{link}/p"
            product_desp['url'] = url
            # append product to md_products

            md_products['maxi_despensa']['products'].append(product_desp)
            
            i += 1

        return md_products

    def safe_get(self, data, *keys, default=None):
        for key in keys:
            try:
                data = data[key]
            except (KeyError, IndexError, TypeError):
                return default
        return data

