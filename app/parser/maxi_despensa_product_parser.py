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
                    "price": "",
                    "img" : "",
                    "offerHighlight": [],
                    "url" : "",
                    "brand" : "",
                    "category" : {
                        "name" : "",
                        "subcategory" : {
                            "name" : ""
                        },
                        "department" : ""
                    }

			} 
            # print(i, ".", product['productName'])
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
            # setting brand
            product_desp['brand'] = self.safe_get(product, "brand")
            # getting categories
            categories = self.safe_get(product, "categories", 0)
            categories_dict = parse_category(categories)
            # setting categories
            product_desp['category']['name'] = categories_dict['category']
            product_desp['category']['subcategory']['name'] = categories_dict['subcategory']
            product_desp['category']['department'] = categories_dict['department']
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


def parse_category(category):
    categories = category.split("/")
    categories_dict = {
            "category" : "", 
            "subcategory" : "",
            "department" : ""
    }

    categories_dict['category'] = categories[1]
    categories_dict['subcategory'] = categories[2]
    categories_dict['department'] = categories[3]

    return categories_dict
